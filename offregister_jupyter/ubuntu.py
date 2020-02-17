from os import environ

from fabric.context_managers import shell_env
from fabric.contrib.files import exists
from fabric.operations import run, sudo
from offregister_fab_utils.apt import apt_depends

from offregister_jupyter.systemd import install_jupyter_notebook_server
import offregister_nginx_static.ubuntu as nginx


def install_jupyter_notebook0(virtual_env=None, *args, **kwargs):
    home = kwargs.get('HOMEDIR', run('echo $HOME', quiet=True))
    virtual_env = virtual_env or '{home}/venvs/jupyter'.format(home=home)

    if not exists(virtual_env):
        apt_depends('python3-pip', 'python3-venv')
        sudo('pip3 install -U pip wheel setuptools')
        run('mkdir -p {}'.format(virtual_env))
        run('python3 -m venv {}'.format(virtual_env))

    with shell_env(VIRTUAL_ENV=virtual_env, PYTHONPATH=virtual_env,
                   PATH="{virtual_env}/bin:$PATH".format(virtual_env=virtual_env)):
        run('pip3 install -U pip wheel setuptools')
        run('pip3 install -U jupyter')

    user, group = (lambda ug: (ug[0], ug[1]) if len(ug) > 1 else (ug[0], ug[0]))(
        run('''printf '%s\t%s' "$USER" "$GROUP"''', quiet=True, shell_escape=False).split('\t'))
    notebook_dir = kwargs.get('notebook_dir', '{home}/notebooks'.format(home=home))
    run("mkdir -p '{notebook_dir}'".format(notebook_dir=notebook_dir))

    return install_jupyter_notebook_server(
        pythonpath=virtual_env,
        notebook_dir=notebook_dir,
        listen_ip='127.0.0.1',  # kwargs['public_ipv4'],
        listen_port=int(kwargs.get('listen_port', '8888')),
        Environments='Environment=VIRTUAL_ENV={virtual_env}\n'
                     'Environment=PYTHONPATH={virtual_env}'.format(virtual_env=virtual_env),
        User=user, Group=group,
        extra_opts=' '.join(("--NotebookApp.password='{password}'".format(password=environ['PASSWORD']),
                             '--NotebookApp.password_required=True',
                             '--NotebookApp.iopub_data_rate_limit=2147483647',  # send output for longer
                             '--no-browser', '--NotebookApp.open_browser=False'))
    )


def setup_nginx1(domain, *args, **kwargs):
    sites_enabled = kwargs.get('sites-enabled', '/etc/nginx/sites-enabled')
    return nginx.setup_conf0(nginx_conf='proxy-pass.conf',
                             SERVER_NAME=domain,
                             SERVER_LOCATION='127.0.0.1:{}'.format(kwargs.get('listen_port', '8888')),
                             NAME_OF_BLOCK='jupyter',
                             ROUTE_BLOCK='# blank',
                             conf_remote_filename='{}/{}'.format(sites_enabled, domain.replace('/', '-')),
                             skip_nginx_restart=False)
