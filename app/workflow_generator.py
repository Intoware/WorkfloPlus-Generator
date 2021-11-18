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
import lxml.etree as et
from datetime import datetime
import uuid

from models import ImportStep, StepType, DecisionPath

START_STEP_INDEX = -1
END_STEP_INDEX = -2


def append_element(xml, tag, text):
    new_element = et.Element(tag)
    new_element.text = text
    xml.append(new_element)


def flatten_to_list(list_of_lists):
    return [
        item for sublist in list_of_lists for item in sublist if bool(item)
    ]


class BaseConnection():

    def __init__(self, source, sink, connection_type=""):
        self.source = source
        self.sink = sink
        self.connection_type = connection_type
        self.connection_id = str(uuid.uuid1())


class StepGroup():

    def __init__(self, import_steps, title, description):

        self.title = str(title) if title else ""
        self.description = str(description) if description else ""

        import_steps.insert(
            0,
            ImportStep(
                step_index=START_STEP_INDEX,
                step_title="Start",
                step_type=StepType.start
            )
        )        
        import_steps.append(
            ImportStep(
                step_index=END_STEP_INDEX,
                step_title="End",
                step_type=StepType.end
            )
        )

        self.step_index_ordered = [z.step_index for z in import_steps]
        self.step_index_to_id = {z.step_index: z.step_id or str(uuid.uuid4()) for z in import_steps}

        self.steps = self._convert_steps(import_steps)
    
    def _check_step_indexes_are_unique(self, import_steps):
        step_indexes = [x.step_index for x in import_steps]
        if len(set(step_indexes)) != len(step_indexes):
            raise HTTPException(
                422, "All StepIndex values must be unique with a group")

    def _convert_steps(self, import_steps):

        # create a decision path (which will get turned into a connection) for steps where none is defined
        # this decision path will point at the next step according to the order in which they were written
        for import_step in import_steps:
            if not import_step.decision_paths and import_step.step_type != StepType.end:
                pos_in_list = self.step_index_ordered.index(
                    import_step.step_index)
                next_step_index = self.step_index_ordered[pos_in_list + 1]
                import_step.decision_paths = [
                    DecisionPath(
                        step_index=next_step_index,
                        decision_name=''
                    )
                ]

        # convert each decision path into a connection
        # create a list of tuples for each import step combined with the connections
        # for that step
        import_steps_with_connections = []
        for import_step in import_steps:
            if import_step.decision_paths:
                this_step_connections = [
                    BaseConnection(
                        self.step_index_to_id[import_step.step_index],
                        self.step_index_to_id[z.step_index],
                        z.decision_name
                    )
                    for z in import_step.decision_paths
                ]
            import_steps_with_connections.append((import_step, this_step_connections))
        
        # convert each import step to a step
        return [self._process_step(import_step, connections) for (import_step, connections) in import_steps_with_connections]

    def _process_step(self, import_step, connections):
        if import_step.step_type == StepType.instruction:
            return BaseStep(import_step.step_title, import_step.step_description, import_step.step_index, step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections)
        if import_step.step_type == StepType.text:
            return InputStep(import_step.step_title, import_step.step_description, import_step.step_index, "Text", step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.numeric:
            return InputStep(import_step.step_title, import_step.step_description, import_step.step_index, "Numeric", step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.photo:
            return InputStep(import_step.step_title, import_step.step_description, import_step.step_index, "Photo", step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.video:
            return InputStep(import_step.step_title, import_step.step_description, import_step.step_index, "Video", step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.signature:
            return InputStep(import_step.step_title, import_step.step_description, import_step.step_index, "Signature", step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.barcode:
            return InputStep(import_step.step_title, import_step.step_description, import_step.step_index, "Barcode", step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.datetime:
            return DateTimeStep(import_step.step_title, import_step.step_description, import_step.step_index, step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"))
        if import_step.step_type == StepType.selection:
            return SelectionStep(import_step.step_title, import_step.step_description, import_step.step_index, import_step.selection_options, step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, optional=import_step.config.get("optional"), fixed=import_step.config.get("fixed"), multi=import_step.config.get("multi"), dynamic=import_step.config.get("dynamic"))
        if import_step.step_type == StepType.decision:
            return DecisionStep(import_step.step_title, import_step.step_description, import_step.step_index, import_step.decision_paths, step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections)
        if import_step.step_type == StepType.group:
            return GroupStep(import_step.step_title, import_step.step_description, import_step.step_index, import_step.steps, step_id=self.step_index_to_id[import_step.step_index], step_tag=import_step.step_tag, connections=connections, is_form=import_step.config.get("form"))
        if import_step.step_type == StepType.start:
            return StartStep(import_step.step_title, import_step.step_description, import_step.step_index, step_id=self.step_index_to_id[import_step.step_index], connections=connections)
        if import_step.step_type == StepType.end:
            return TerminatorStep(import_step.step_title, import_step.step_description, import_step.step_index, step_id=self.step_index_to_id[import_step.step_index])
        return BaseStep(import_step.step_title, import_step.step_description, import_step.step_index, import_step.step_id, connections=connections)

    def return_xml(self):
        # this calls the construct_xml method on each step
        # the xml for all of the steps sits within an xml element called "Steps"
        steps_xml = et.Element("Steps")
        for i, step in enumerate(self.steps):
            steps_xml.append(step.construct_xml(i))
        return steps_xml


class Workflow(StepGroup):

    def __init__(self, import_steps, title, description):
        super().__init__(import_steps, title, description)
        self.workflow_id = str(uuid.uuid1())

    def return_xml(self):
        # this calls the return_xml method on the StepGroup
        # and then adds all of the other information required
        # at the workflow level
        steps_xml = super().return_xml()
        workflow_xml = et.Element("Procedure", IsReport="false")
        append_element(workflow_xml, "ID", self.workflow_id)
        append_element(workflow_xml, "Title", self.title)
        append_element(workflow_xml, "Description", self.description)
        append_element(workflow_xml, "DocVersion", "")
        append_element(workflow_xml, "Version", "")
        append_element(workflow_xml, "Author", "")
        append_element(workflow_xml, "Metadata", "")
        append_element(workflow_xml, "Interlocked", "false")
        et.SubElement(workflow_xml, "Report", Export="false")
        append_element(workflow_xml, "DateModified",
                       datetime.now().isoformat())
        capabilities_xml = et.Element("Capabilities")
        capabilities = ["Default", "Freeform", "Form", "FileInput", "PDFAsset"]
        for capability in capabilities:
            append_element(capabilities_xml, "Capability", capability)
        workflow_xml.append(capabilities_xml)
        workflow_xml.append(steps_xml)
        return workflow_xml


class BaseStep():

    def __init__(self, title, description, step_index, step_id, step_tag="", connections=None):
        self.title = str(title)
        if description is not None:
            self.description = str(description)
        else:
            self.description = ""
        self.step_index = step_index
        self.step_type = "ConfirmStep"
        self.step_id = step_id
        self.step_tag = step_tag
        self.connections = connections

    def _connections_element(self, connection_object):
        result = et.Element(
            "Connection",
            Type=connection_object.connection_type,
            ID=connection_object.connection_id,
            Source=connection_object.source,
            Sink=connection_object.sink
        )
        return result

    def _connection_anchors_element(self, connection_object):
        result = et.Element(
            "Connection",
            ID=connection_object.connection_id,
            Anchor="Bottom|Top"
        )
        return result

    def _construct_connections_xml(self, connections):
        connections_xml = et.Element("Connections")
        for step_connection in connections:
            connections_xml.append(self._connections_element(step_connection))
        return connections_xml

    def _construct_connection_anchors_xml(self, connections):
        connections_xml = et.Element("ConnectionAnchors")
        for step_connection in connections:
            connections_xml.append(
                self._connection_anchors_element(step_connection))
        return connections_xml

    def construct_xml(self, step_number):
        step_xml = et.Element("Step", Type=self.step_type)
        base_xml = et.Element("Base", ID=self.step_id)
        append_element(base_xml, "Title", self.title)
        append_element(base_xml, "Description", self.description)
        if self.step_tag:
            append_element(base_xml, "Tag", self.step_tag)
        if self.connections:
            base_xml.append(self._construct_connections_xml(self.connections))
        designer_xml = et.Element("DesignerData")
        append_element(designer_xml, "Position",
                       "50," + str((1 + step_number) * 100))
        append_element(designer_xml, "Size", "0,0")
        if self.connections:
            designer_xml.append(
                self._construct_connection_anchors_xml(self.connections)
                )
        base_xml.append(designer_xml)
        step_xml.append(base_xml)
        return step_xml


class StartStep(BaseStep):
    def __init__(self, title, description, step_index, step_id, connections):
        super().__init__(title, description, step_index, step_id=step_id,
                         connections=connections)
        self.step_type = "StartStep"


class TerminatorStep(BaseStep):
    def __init__(self, title, description, step_index, step_id):
        super().__init__(title, description, step_index, step_id=step_id)
        self.step_type = "TerminateGroupStep"


class DecisionStep(BaseStep):
    def __init__(self, title, description, step_index, decision_paths, connections, step_id=None, step_tag=""):
        super().__init__(title, description, step_index, step_id=step_id,
                         step_tag=step_tag, connections=connections)
        self.step_type = "DecisionStep"


class InputStep(BaseStep):
    def __init__(self, title, description, step_index, input_type, connections, step_id=None, step_tag="", decision_paths=None, optional=None):
        super().__init__(title, description, step_index, step_id=step_id,
                         step_tag=step_tag, connections=connections)
        self.step_type = "InputStep"
        self.input_type = str(input_type)
        self.optional = optional if not optional is None else "False"

    def construct_xml(self, step_number):
        step_xml = super().construct_xml(step_number)
        append_element(step_xml, "InputType", self.input_type)
        append_element(step_xml, "IsOptional", str(self.optional).lower())
        constraint_element = et.Element("Constraint")
        append_element(constraint_element, "ConstraintType", "None")
        ip_element = et.Element("InputParameter")
        ip_element.append(constraint_element)
        step_xml.append(ip_element)
        return step_xml


class DateTimeStep(BaseStep):
    def __init__(self, title, description, step_index, connections, step_id=None, step_tag="", decision_paths=None, optional=None):
        super().__init__(title, description, step_index, step_id=step_id,
                         step_tag=step_tag, connections=connections)
        self.step_type = "InputStep"
        self.input_type = "DateTime"
        self.optional = optional if not optional is None else "False"

    def construct_xml(self, step_number):
        step_xml = super().construct_xml(step_number)
        append_element(step_xml, "InputType", self.input_type)
        append_element(step_xml, "IsOptional", str(self.optional).lower())
        constraint_element = et.Element("Constraint")
        append_element(constraint_element, "DisplayDate", "true")
        append_element(constraint_element, "DisplayTime", "true")
        ip_element = et.Element("InputParameter")
        ip_element.append(constraint_element)
        step_xml.append(ip_element)
        return step_xml


class SelectionStep(BaseStep):
    def __init__(self, title, description, step_index, choices, connections, step_id=None, step_tag="", decision_paths=None, optional=False, fixed=None, multi=None, dynamic=None):
        super().__init__(title, description, step_index, step_id=step_id,
                         step_tag=step_tag, connections=connections)
        self.step_type = "InputStep"
        self.input_type = "Selection"
        self.choices = choices
        self.optional = optional if not optional is None else "False"
        self.fixed = fixed if not fixed is None else "true"
        self.multi = multi if not multi is None else "false"
        self.dynamic = dynamic

    def construct_xml(self, step_number):
        step_xml = super().construct_xml(step_number)
        append_element(step_xml, "InputType", self.input_type)
        append_element(step_xml, "IsOptional", str(self.optional).lower())
        ip_element = et.Element("InputParameter")
        ip_element.append(et.Element("Constraint"))
        choice_element = et.Element("Choices")
        if bool(self.dynamic):
            append_element(step_xml, "DynamicUrl", self.choices[0])
        else:
            for choice in self.choices:
                append_element(choice_element, "Choice", choice.strip())
        ip_element.find("Constraint").append(choice_element)
        append_element(ip_element.find("Constraint"),
                       "FixedMode", str(self.fixed).lower())
        append_element(ip_element.find("Constraint"), "MinSelection", "1")
        max_selection = "1" if self.multi == "false" else str(
            len(self.choices))
        append_element(ip_element.find("Constraint"),
                       "MaxSelection", max_selection)
        step_xml.append(ip_element)
        return step_xml


class GroupStep(BaseStep):
    def __init__(self, title, description, step_index, step_steps, connections, step_id=None, step_tag="", decision_paths=None, is_form=None):
        super().__init__(title, description, step_index, step_id=step_id,
                         step_tag=step_tag, connections=connections)
        self.step_type = "GroupStep"
        self.is_form = is_form if not is_form is None else "false"
        self.step_group = StepGroup(step_steps, title, description)

    def construct_xml(self, step_number):
        step_xml = super().construct_xml(step_number)
        steps_xml = self.step_group.return_xml()
        step_xml.append(steps_xml)
        step_xml.attrib["IsReport"] = self.is_form.lower()
        return step_xml
