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

from fastapi import HTTPException
import pandas as pd

from models import *

STEP_ID = "StepId"
STEP_INDEX = "StepIndex"
STEP_TITLE = "StepTitle"
STEP_DESCRIPTION = "StepDescription"
STEP_TAG = "StepTag"
STEP_TYPE = "StepType"
DECISION_PATHS = "DecisionPaths"
SELECTION_OPTIONS = "SelectionOptions"
CONFIG = "Config"
PARENT = "Parent"
PARENT_DEPTH = "ParentDepth"


def _field_conversions(imported_steps_df):

    # convert any NaNs to empty strings for easier error handling
    imported_steps_df.fillna(value="", inplace=True)

    # step type strings converted to enums
    imported_steps_df[STEP_TYPE] = imported_steps_df[STEP_TYPE].apply(
        lambda x: StepType[x.strip().lower()]
    )

    # convert decision_paths to pairs
    if DECISION_PATHS in imported_steps_df.columns:
        imported_steps_df[DECISION_PATHS] = imported_steps_df[DECISION_PATHS].apply(
            lambda x:
            [
                DecisionPath(
                    step_index=int(z.split(":")[1].strip()),
                    decision_name=z.split(":")[0].strip()
                )
                for z in x.split(";")
            ]
            if not x == ""
            else None
        )

    # convert selection options to list
    if SELECTION_OPTIONS in imported_steps_df.columns:
        imported_steps_df[SELECTION_OPTIONS] = imported_steps_df[SELECTION_OPTIONS].apply(
            lambda x: x.split(";")
        )

    # convert config to dict
    if CONFIG in imported_steps_df.columns:
        imported_steps_df[CONFIG] = imported_steps_df[CONFIG].apply(
            lambda x:
            {
                str(z.split(":")[0].strip().lower()): str(z.split(":")[1].strip())
                for z in x.split(";")
            }
            if not x == ""
            else {}
        )

    # convert Parent (i.e. the StepIndex of the Parent) to int
    if PARENT in imported_steps_df.columns:
        imported_steps_df[PARENT] = pd.to_numeric(
            imported_steps_df[PARENT], errors="coerce")

    return imported_steps_df


def _arrange_steps_under_parents(imported_steps_df, workflow_steps):

    depth = 0
    hit_bottom = False
    # set 0 on steps with no parents
    imported_steps_df.loc[
        imported_steps_df[PARENT].apply(lambda x: x != x),
        PARENT_DEPTH
    ] = int(0)

    while not hit_bottom:
        # loop through each level down
        # until there are no steps at a given level

        mask_parent_depth = imported_steps_df[PARENT_DEPTH].apply(
            lambda x: x == depth
            )

        level_above_indexes = imported_steps_df.loc[
            mask_parent_depth,
            STEP_INDEX
        ].astype("int").values

        depth += 1

        mask_parent_is_1_above = imported_steps_df[PARENT].apply(
                lambda x: x in level_above_indexes
                )
        if not any(mask_parent_is_1_above):
            hit_bottom = True
            break

        imported_steps_df.loc[
            mask_parent_is_1_above,
            PARENT_DEPTH
        ] = int(depth)
   
    max_depth = int(imported_steps_df[PARENT_DEPTH].max())

    for i in range(max_depth, 0, -1):
        depth_df = imported_steps_df[imported_steps_df[PARENT_DEPTH] == i]
        for j, row in depth_df.iterrows():
            step_index = int(row[STEP_INDEX])
            parent_step_index = int(row[PARENT])

            step = [x for x in workflow_steps if x.step_index == step_index][0]
            parent_step = [
                x for x in workflow_steps if x.step_index == parent_step_index][0]

            if parent_step.steps is None:
                parent_step.steps = []
            parent_step.steps.append(step)
            workflow_steps.remove(step)

    return workflow_steps


def convert_csv_to_import_steps(imported_steps_df):

    # convert string type fields from the csv into required types
    imported_steps_df = _field_conversions(imported_steps_df)

    # create a flat list of ImportStep
    df_json = imported_steps_df.to_dict("records")
    workflow_steps = [
        ImportStep(
            step_id=row.get(STEP_ID),
            step_index=row.get(STEP_INDEX),
            step_title=row.get(STEP_TITLE),
            step_description=row.get(STEP_DESCRIPTION) if not row.get(
                STEP_DESCRIPTION) is None else "",
            step_tag=row.get(STEP_TAG) if not row.get(
                STEP_TAG) is None else "",
            step_type=row.get(STEP_TYPE) if not row.get(
                STEP_TYPE) is None else StepType.instruction,
            decision_paths=row.get(DECISION_PATHS) if not row.get(
                DECISION_PATHS) is None else None,
            selection_options=row.get(SELECTION_OPTIONS) if not row.get(
                SELECTION_OPTIONS) is None else None,
            config=row.get(CONFIG) if not row.get(CONFIG) is None else {}
        )
        for row in df_json
    ]

    # next recurse the steps to put each step with a parent
    # in the ImportStep list of that parent step
    if PARENT in imported_steps_df.columns:
        workflow_steps = _arrange_steps_under_parents(
            imported_steps_df,
            workflow_steps
        )

    return workflow_steps
