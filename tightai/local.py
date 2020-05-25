# AUTOGENERATED! DO NOT EDIT! File to edit: 07_local.ipynb (unless otherwise specified).

__all__ = ['load_run_handler', 'read_root', 'server_app', 'parse_cli_args', 'local_server']

# Cell
import os
import json
import importlib.util

import argparse

try:
    import fastapi
except:
    raise Exception(f"Dependancies missing.To use the tightai.local dev server, please install:\n\npip install fastapi uvicorn python-multipart\n\nor\n\npipenv install fastapi uvicorn python-multipart")

from fastapi import FastAPI, Body, File, UploadFile, Response, status
from starlette.requests import Request
from typing import List
from urllib.parse import parse_qs
from pathlib import Path
import uvicorn

global app_run

def load_run_handler(base_dir):
    global app_run
    entry_file='entry.py'
    base_dir = Path(base_dir)
    if base_dir.is_file():
        raise Exception(f"{base_dir} must be a directory")
    path = Path(base_dir) / entry_file
    if not path.exists() and not path.is_file():
        raise Exception(f"{path} not found. You must have `entry.py` in the root of your project.")
    spec = importlib.util.spec_from_file_location("entry", path)
    entry_module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(entry_module)
    except ModuleNotFoundError as e:
        # print(e.name, e.args)
        print(f"The package `{e.name}` is not found in your project's local path.\n\nIs it installed? \nDid you activate your virtual environment?\n\nAre you running the tight localserver in the root of your project?")
        return
    app_run = entry_module.run

# Cell
server_app = FastAPI()

@server_app.get("{path:path}")
@server_app.post("{path:path}")
@server_app.put("{path:path}")
@server_app.delete("{path:path}")
async def read_root(path: str,
        request: Request,
        response: Response
    ):
    headers = request.headers
    query_params = parse_qs(str(request.query_params))
    method = request.method
    json_data = {}
    try:
        json_data = await request.json()
    except:
        pass
    form = await request.form()
    form_data = {}
    file = None
    metadata = {}
    if form != None:
        form_data = dict(form)
        if 'file' in form_data:
            file = form['file'].file.read()
            metadata['filename'] = form['file'].filename
            metadata['file_size'] = len(file)
            del form_data['file']
    app_response =  app_run(json_data=json_data,
                query_params=query_params,
                path=path,
                form_data=form_data,
                file=file,
                headers=headers,
                method=method,
                metadata=metadata,
        )
    if "status" in app_response:
        status = app_response['status']
        response.status_code = status
        del app_response['status']
    return app_response

# Cell
def parse_cli_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', type=int, default=5007, help='Default port for the local development server')
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="Directory path to the the location for your `entry.py` module; typically in the root of your project.",
    )
    path = Path(".")
    port = 5007
    try:
        args = parser.parse_args()
        path = args.dir
        port = args.port
    except:
        pass
    return path, port

def local_server(path=".", port='5007'):
    load_run_handler(path)
    uvicorn.run(server_app, host="localhost", port=port)

# Cell
if __name__ == "__main__":
    path, port = parse_cli_args()
    if path and port:
        local_server(path=path, port=port)