from app.bootstrap import bootstrap_local_dependencies

bootstrap_local_dependencies()

from app.ui.main_window import launch_app


if __name__ == "__main__":
    raise SystemExit(launch_app())
