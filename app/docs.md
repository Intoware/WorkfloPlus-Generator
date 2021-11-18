# The WorkfloPlus Workflow Generator

The objective of the WorkfloPlus Workflow Generator application is to provide a more convenient means of mass creation of WorkfloPlus Workflows; either as a standalone tool or as the last component of a wider document to workflow conversion.

## User Documentation

Currently there is no front-end to the WorkfloPlus Workflow Generator; the functionality can be accessed via the API.

It is recommended to use a tool such as Postman; this is the tool refered to in the documentation.

## CSV Structure

Each row in the CSV represents a step in the workflow

### StepIndex column [mandatory]
The StepIndex column should be populated with a positive and unique Integer value for each row

### StepTitle column [mandatory]
The StepTitle column should be populated with Text that will be used as the Title for each Step

### StepDescription column [optional]
The StepDescription column can be populated with Text that will be used as the Description for each Step

### StepTag column [optional]
The StepTag column can be populated with Text that will be used as the Tag for each Step

### StepType column [mandatory]
The StepType column can be populated with Text that will be used as the Type for each Step.
Supported Types are:
* Instruction
* Text
* Numeric
* Photo
* Video
* Signature
* Barcode
* Selection
* Decision
* Group

### DecisionPaths column [optional]
The DecisionPaths column is optional; in the absence of the column the WorkfloPlus Workflow Generator will treat the process as linear, adding steps to the Workflow in the order in which they appear in the CSV. For any row where the DecisionPaths column is empty the Step for that row will be connected to the next Step in the CSV.
In order to define one or more Decision Paths for a given Step, populate the DecisionPaths with a semicolon-seperated list of the format "{DecisionName}:{StepIndex},{DecisionName}:{StepIndex}", for example "Yes:10,No:2" will create two decision paths from the Step in question, the answer "Yes" will take the user to the Step corresponding to StepIndex 10 whilst the answer "No" will take the user to the Step corresponding to StepIndex 2.

N.B terminate steps are not represented in the CSV, and the WorkfloPlus Workflow Generator is constrainted to creating Workflows that have a single terminate step at each level, to connect a Decision Path to the terminate step use the specially reserved StepIndex of -2

### SelectionOptions column [optional]
The SelectionOptions column is optional, it applies only to the Selection Type Step; used to define the Options for a Selection step by way of a semicolon-seperated list, if SelectionOptions are not provided for a Selection step it will default to having the SelectionOptions "Yes" or "No"

### Config column [optional]
The Config column covers varies options and settings on different step types, in order to avoid having too many different columns

#### Input Step
Used to define whether the step is optional or not
* Optional: True/False (default to False)

#### Group Step
Used to define the type of Group, the following types are supported
* Form: True/False (defaults to False)

#### Selection Step
Used to define the type of Group, the following types are supported, if an Option is not provided it will default to the Default type
* Fixed: True/False (defaults to True)
* Multi: True/False (defaults to False)

### Parent [optional]
If a given Step belongs to a Group, the Parent column is used to define the StepIndex of the Group Step to which the Step in question belongs

### StepId [optional]
It may be useful to define the Id of certain steps if you wish to make a dynamic variable or collection reference to one of them later in the workflow

[Copyright © Intoware Limited, 2021]:#

[This file is part of WorkfloPlusWorkflowGenerator.]:#

[WorkfloPlusWorkflowGenerator is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.]:#

[WorkfloPlusWorkflowGenerator is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.]: #

[You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.]: #