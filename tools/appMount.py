from fastapi.staticfiles import StaticFiles #静态文件操作
def staticMount(app):
    # 静态文件
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/upload", StaticFiles(directory="upload"), name="upload")
    return app