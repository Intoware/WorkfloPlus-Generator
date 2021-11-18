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

from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from humps import camelize


def to_camel(string):
    return camelize(string)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class StepType(str, Enum):
    instruction = "instruction"
    text = "text"
    numeric = "numeric"
    photo = "photo"
    video = "video"
    signature = "signature"
    barcode = "barcode"
    selection = "selection"
    decision = "decision"
    group = "group"
    datetime = "datetime"
    start = "start"
    end = "end"

    @classmethod
    def _missing_(cls, value):
        return StepType.instruction


class DecisionPath(CamelModel):
    step_index: int
    decision_name: str


class ImportStep(CamelModel):
    step_id: str = None
    step_index: int
    step_title: str = "Step Title"
    step_description: str = ""
    step_tag: str = ""
    step_type: StepType = StepType.instruction
    decision_paths: Optional[List[DecisionPath]]
    selection_options: Optional[List[str]]
    steps: Optional[List["ImportStep"]]
    config: dict = {}


# this call is to handle the recursive nature of the ImportStep
# model, which itself contains a list of ImportStep
ImportStep.update_forward_refs()


class ImportWorkflow(CamelModel):
    workflow_title: str
    workflow_description: Optional[str] = ""
    workflow_steps: List[ImportStep]
