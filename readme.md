# Workflow Generator

The workflow generator application converts a representation of a series of steps into a zip file containing an xml file that can be uploaded as a workflow for use with WorkfloPlus.

This application is intended to reduce the amount of bespoke effort required to automatically convert user files or documents to WorkfloPlus workflows.

Two endpoints are provided for the upload of the series of steps for conversion
* CSV format
* JSON format

If the JSON format endpoint is used it is immediately converted into a list of the model type ImportStep
However if the CSV format endpoint is used then a more involved method is used to convert firstly the csv strings into the correct field types and then the flat representation into a nested model that reflects the parent/child relationships of the steps

After that the steps, along with the workflow title and description are used to construct a representation of the workflow; firstly this involves mapping each ImportStep to an object that represents the full definition of a step within a workflow xml file, secondly this involves creating all of the connections - both those that are specified in the file and those that can be infered

N.B The import files should not include reference to start and end/terminate steps, these are added as required by the application

Once the Workflow object has been created, the return_xml method is called, this will return an xml file according to the defintion of the Workflow object

Finally the xml file is added to a zip file and returned as a byte stream

## Feedback

Please do get in contact with Intoware Ltd via support@intoware.com to raise any bugs or issues, or to suggest improvements or new features; please make it clear which product you are refering to when raising the ticket.

[Copyright © Intoware Limited, 2021]:#

[This file is part of WorkfloPlusWorkflowGenerator.]:#

[WorkfloPlusWorkflowGenerator is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.]:#

[WorkfloPlusWorkflowGenerator is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.]: #

[You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.]: #