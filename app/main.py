# Copyright © Intoware Limited, 2021
#
# This file is part of WorkfloPlusWorkflowGenerator.
#
# WorkfloPlusWorkflowGenerator is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# WorkfloPlusWorkflowGenerator is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. 
# If not, see <https://www.gnu.org/licenses/>.

from fastapi import FastAPI, HTTPException, File, UploadFile, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from typing import Optional
import pandas as pd
import markdown

from models import *

from workflow_generator import Workflow
from zip_converter import construct_zip
from csv_to_import_steps import convert_csv_to_import_steps

app = FastAPI()


@app.get("/")
async def root():
    return {"ServiceName": "WorkfloPlus Workflow Generator"}


@app.get("/userguide")
async def userguide():
    filepath = "docs.md"
    with open(filepath, "r", encoding="utf-8") as input_file:
        text = input_file.read()
    html = markdown.markdown(text)
    return HTMLResponse(html, 200)


@app.post("/api/json/v1")
async def convert_json_v1(
    workflow_definition: ImportWorkflow
    #files: List[UploadFile] = File(...)
):
    return convert_to_workflow(
        workflow_definition.workflow_steps,
        workflow_definition.workflow_title,
        workflow_definition.workflow_description,
    )


@app.post("/api/csv/v1")
def convert_csv_v1(
    workflow_title: str,
    workflow_description: Optional[str] = "",
    workflow_steps: UploadFile = File(...)
):

    try:
        workflow_steps.file.seek(0)
        workflow_steps_df = pd.read_csv(workflow_steps.file)
    except Exception as e:
        raise HTTPException(422, e)

    workflow_steps = convert_csv_to_import_steps(workflow_steps_df)

    return convert_to_workflow(
        workflow_steps,
        workflow_title,
        workflow_description,
    )


def convert_to_workflow(workflow_steps, workflow_title, workflow_description):

    if workflow_title is None:
        workflow_title = "My Workflow"

    if workflow_description is None:
        workflow_description = ""

    workflow_object = Workflow(
        workflow_steps, workflow_title, workflow_description
    )

    workflow_xml = workflow_object.return_xml()

    new_workflow_zip_buffer = construct_zip(
        workflow_xml
    )

    return StreamingResponse(
        new_workflow_zip_buffer,
        200,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment;filename=workflow.zip"}
    )
