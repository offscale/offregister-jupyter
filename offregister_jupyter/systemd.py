from offregister_fab_utils.ubuntu.systemd import (
    install_upgrade_service,
    restart_systemd,
)


def install_jupyter_notebook_server(
    listen_ip,
    notebook_dir,
    pythonpath,
    listen_port="8888",
    conf_name="jupyter_notebook",
    extra_opts=None,
    **kwargs
):
    install_upgrade_service(
        conf_name,
        conf_local_filepath=kwargs.get("systemd-conf-file"),
        context={
            "ExecStart": " ".join(
                (
                    "{pythonpath}/bin/jupyter notebook".format(pythonpath=pythonpath),
                    "--NotebookApp.notebook_dir='{notebook_dir}'".format(
                        notebook_dir=notebook_dir
                    ),
                    "--NotebookApp.ip={listen_ip}".format(listen_ip=listen_ip),
                    "--NotebookApp.port={listen_port}".format(listen_port=listen_port),
                    "--Session.username={User}".format(User=kwargs["User"]),
                    extra_opts if extra_opts else "",
                )
            ),
            "Environments": kwargs["Environments"],
            "WorkingDirectory": pythonpath,
            "User": kwargs["User"],
            "Group": kwargs["Group"],
        },
    )
    return restart_systemd(conf_name)
