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

import lxml.etree as et
import os
import io
import zipfile
import logging
import tempfile
import shutil


def zip_path(path):

    # Check path exists
    if not path or not os.path.exists(path):
        logging.warning("No files/folders to add, not creating zip file")
        return None

    logging.debug("Creating zip file")
    zip_stream = io.BytesIO()
    try:
        zfile = zipfile.ZipFile(
            zip_stream, 'w', compression=zipfile.ZIP_DEFLATED
        )
    except EnvironmentError as e:
        logging.warning("Couldn't create zip file")
        return None

    if os.path.isdir(path):
        root_len = len(os.path.abspath(path))

        # Walk through the directory, adding all files
        for root, dirs, files in os.walk(path):
            archive_root = os.path.abspath(root)[root_len:]
            for f in files:
                fullpath = os.path.join(root, f)
                archive_name = os.path.join(archive_root, f)
                try:
                    zfile.write(
                        fullpath, archive_name, zipfile.ZIP_DEFLATED
                    )
                except EnvironmentError as e:
                    logging.warning("Couldn't add file: %s", (str(e),))
    else:
        # Exists and not a directory, assume a file
        try:
            zfile.write(path, os.path.basename(path), zipfile.ZIP_DEFLATED)
        except EnvironmentError as e:
            logging.warning("Couldn't add file: %s", (str(e),))
    zfile.close()
    zip_stream.seek(0)
    return zip_stream


def construct_zip(workflow_xml):
    temp_dir = tempfile.mkdtemp()
    workflow_bytes_string = et.tostring(workflow_xml, pretty_print=True)
    with open(os.path.join(temp_dir, 'workflow.xml'), 'wb') as f:
        f.write(workflow_bytes_string)
    buf = zip_path(temp_dir)
    shutil.rmtree(temp_dir)
    return buf
