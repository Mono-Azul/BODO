# BODE - A production data explorer
#
# Copyright (C) 2024  Jens Hofer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime

import pymssql
from dataclasses import dataclass

from setuptools.package_index import parse_requirement_arg

conn = None

def check_and_connect(server, user, pw, db):
    global conn
    conn = pymssql.connect(server, user, pw, "IFACE")

@dataclass()
class Area:
    area_id: int
    area: str

@dataclass()
class Parameter:
    element_id: int
    parameter_name: str
    preset_val_recipe: str
    preset_val_batch: str
    actual_val: str
    uom: str

@dataclass()
class SubPhase:
    prid: int
    element_id: int
    element_parent_id: int
    equipment_name: str
    subphase_name: str
    subphase_node: int
    subphase_no: int
    subphase_status: str
    actual_start: datetime
    actual_end: datetime
    duration: int

@dataclass()
class Phase:
    prid: int
    element_id: int
    element_parent_id: int
    equipment_name: str
    phase_name: str
    phase_node: int
    phase_no: int
    phase_status: str
    actual_start: datetime
    actual_end: datetime
    duration: int

    subphases: list[SubPhase]

@dataclass()
class UnitProcedure:
    prid: int
    element_id: int
    equipment_name: str
    unit_procedure_name: str
    unit_procedure_node: int
    unit_procedure_no: int
    unit_procedure_status: str
    actual_start: datetime
    actual_end: datetime
    duration: int

    phases: list[Phase]

@dataclass()
class Batch:
    language: str
    prid: int
    batch: str
    product: str
    planned_start: datetime
    actual_start: datetime
    actual_end: datetime
    recipe: str
    recipe_version: str
    area_id: int
    area_name: str
    barea_id: int
    barea_name: str

    unit_procedures: list[UnitProcedure]

    unit_procedures_loaded: bool = False
    phases_loaded: bool = False
    subphases_loaded: bool = False

sqlcmd_batch = """SELECT TOP 1000 ba.PRID
                    ,ba.Batch
                    ,ISNULL(t1.LANGUAGE_TEXT, PRODUCT) AS Product
                    ,ba.Planned_Start
                    ,ba.Actual_Start
                    ,ba.Actual_End
                    ,ISNULL(t2.LANGUAGE_TEXT, RECIPE_NAME)  AS Recipe
                    ,ba.Recipe_Version
                    ,ba.Area_ID
                    ,ba.BArea_ID
                    ,ISNULL(t3.LANGUAGE_TEXT, AREA.NAME)  AS Area
                    ,ISNULL(t4.LANGUAGE_TEXT, BATCHAREA.NAME) AS Batch_Area
                FROM BATCH ba
                    LEFT JOIN LANGUAGE_TEXT t1
                        ON ba.Product = t1.Reference_Text
                            AND t1.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t2
                        ON ba.Recipe_Name = t2.Reference_Text
                            AND t2.Language = 'EN'
                    INNER JOIN AREA
                        ON ba.Area_ID = Area.AREA_ID
                    LEFT JOIN LANGUAGE_TEXT t3
                        ON AREA.NAME = t3.Reference_Text
                            AND t3.Language = 'EN'
                    INNER JOIN BATCHAREA
                        ON ba.BAREA_ID = BATCHAREA.BAREA_ID
                    LEFT JOIN LANGUAGE_TEXT t4
                        ON BATCHAREA.NAME = t4.Reference_Text
                            AND t4.Language = 'EN'"""

sqlcmd_element = """SELECT be.PRID
                    ,be.Element_ID
                    ,be.Parent_Element_ID
                    ,ISNULL(t1.LANGUAGE_TEXT, be.Equipment_Name) AS Equipment_Name
                    ,ISNULL(t2.LANGUAGE_TEXT, be.Element_Name) AS Element_Name
                    ,be.Element_Node AS Element_Node
                    ,be.Curr_Element_No AS Element_NO
                    ,ISNULL(t3.LANGUAGE_TEXT, be.Element_Status)  AS Element_Status
                    ,be.Actual_Start
                    ,be.Actual_End
                    ,be.Duration
                    ,be.Element_Type
                FROM BATCH_ELEMENT be
                    LEFT JOIN LANGUAGE_TEXT t1
                        ON be.Equipment_Name = t1.Reference_Text
                            AND t1.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t2
                        ON be.Element_Name = t2.Reference_Text
                            AND t2.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t3
                        ON be.Element_Status = t3.Reference_Text
                            AND t3.Language = 'EN'
                WHERE PRID = %s"""

def get_phases(prid, element_parent_id, subphases=False):
    cursor = conn.cursor()

    final_sqlcmd = sqlcmd_element + """ AND be.Parent_Element_ID = %s"""

    cursor.execute(final_sqlcmd, (prid, element_parent_id))

    object_list = []
    saved_cursor = []

    for x in cursor:
        saved_cursor.append(x)

    cursor.close()

    for row in saved_cursor:
        if row[11] == "Phase":
            subphases_list = list()
            if subphases:
                subphases_list = get_phases(prid, row[1])

            up = Phase(
            prid = row[0],
            element_id = row[1],
            element_parent_id = row[2],
            equipment_name = row[3],
            phase_name = row[4],
            phase_node = row[5],
            phase_no = row[6],
            phase_status = row[7],
            actual_start = row[8],
            actual_end = row[9],
            duration = row[10],
            subphases = subphases_list)
        else:
            up = SubPhase(
                prid=row[0],
                element_id=row[1],
                element_parent_id=row[2],
                equipment_name=row[3],
                subphase_name=row[4],
                subphase_node=row[5],
                subphase_no=row[6],
                subphase_status=row[7],
                actual_start=row[8],
                actual_end=row[9],
                duration=row[10])
        object_list.append(up)

    return object_list

def get_unit_procedures(prid, phases=False, subphases=False):
    cursor = conn.cursor()
    final_sqlcmd = sqlcmd_element + """ AND Element_Type = 'Unit Procedure'"""

    cursor.execute(final_sqlcmd, prid)

    saved_cursor = []
    unit_procedure_list = []

    for x in cursor:
        saved_cursor.append(x)

    cursor.close()

    for unitproc in saved_cursor:
        phases_list = list()
        if phases:
            phases_list = get_phases(prid, unitproc[1], subphases)

        up = UnitProcedure(
        prid = unitproc[0],
        element_id = unitproc[1],
        equipment_name = unitproc[3],
        unit_procedure_name = unitproc[4],
        unit_procedure_node = unitproc[5],
        unit_procedure_no = unitproc[6],
        unit_procedure_status = unitproc[7],
        actual_start = unitproc[8],
        actual_end = unitproc[9],
        duration = unitproc[10],
        phases = phases_list)
        unit_procedure_list.append(up)

    return unit_procedure_list



def get_batch(prid: int):
    cursor = conn.cursor()
    final_sqlcmd = sqlcmd_batch + """ WHERE ba.PRID = %s"""
    cursor.execute(final_sqlcmd, prid)

    nb: Batch = None

    for batch in cursor:
        nb = Batch(
        language = "EN",
        prid = batch[0],
        batch = batch[1],
        product = batch[2],
        planned_start = batch[3],
        actual_start = batch[4],
        actual_end = batch[5],
        recipe = batch[6],
        recipe_version = batch[7],
        area_id = batch[8],
        barea_id = batch[9],
        area_name = batch[10],
        barea_name = batch[11],
        unit_procedures= list())
    cursor.close()
    return nb

def get_batches(area_id: int = None, product: str = None, start: datetime = None, end: datetime = None):
    final_sqlcmd = sqlcmd_batch + """ WHERE 1=1"""

    param_tuple = tuple()

    if area_id != None:
        final_sqlcmd = final_sqlcmd + """ AND ba.Area_ID = %s"""
        param_tuple = param_tuple + (area_id,)

    if product != None:
        final_sqlcmd = final_sqlcmd + """ AND ISNULL(t1.LANGUAGE_TEXT, PRODUCT) = %s"""
        param_tuple = param_tuple + (product,)

    if start != None:
        final_sqlcmd = final_sqlcmd + """ AND ba.Actual_Start >= %s"""
        param_tuple = param_tuple + (start,)

    if end != None:
        final_sqlcmd = final_sqlcmd + """ AND ba.Actual_Start < %s"""
        param_tuple = param_tuple + (end,)

    print(final_sqlcmd)
    print(param_tuple)

    cursor = conn.cursor()
    cursor.execute(final_sqlcmd, param_tuple)

    batch_dict = dict()

    for batch in cursor:
        nb = Batch(
        language = "EN",
        prid = batch[0],
        batch = batch[1],
        product = batch[2],
        planned_start = batch[3],
        actual_start = batch[4],
        actual_end = batch[5],
        recipe = batch[6],
        recipe_version = batch[7],
        area_id = batch[8],
        barea_id = batch[9],
        area_name = batch[10],
        barea_name = batch[11],
        unit_procedures= list())
        batch_dict[batch[0]] = nb

    cursor.close()
    return batch_dict

def get_batch_elements(batch: Batch, phases=False, subphases=False):
    batch.unit_procedures_loaded = True
    batch.phases_loaded = phases
    batch.subphases_loaded = subphases

    batch.unit_procedures = get_unit_procedures(batch.prid, phases, subphases)

def get_batch_all_elements(batch: Batch):
    batch.unit_procedures_loaded = True
    batch.phases_loaded = True
    batch.subphases_loaded = True

    cursor = conn.cursor()

    final_sqlcmd = sqlcmd_element + """ ORDER BY be.Element_ID, be.Parent_Element_ID"""

    cursor.execute(final_sqlcmd, batch.prid)

    actual_UP: UnitProcedure = None
    actual_Phase: Phase = None

    for row in cursor:
        if row[11] == "Unit Procedure":
            up = UnitProcedure(
                prid=row[0],
                element_id=row[1],
                equipment_name=row[3],
                unit_procedure_name=row[4],
                unit_procedure_node=row[5],
                unit_procedure_no=row[6],
                unit_procedure_status=row[7],
                actual_start=row[8],
                actual_end=row[9],
                duration=row[10],
                phases= list())

            if actual_Phase != None:
                actual_UP.phases.append(actual_Phase)
                actual_Phase = None

            if actual_UP != None:
                batch.unit_procedures.append(actual_UP)

            actual_UP = up

        if row[11] == "Phase" and row[2] == actual_UP.element_id:
            up = Phase(
                prid=row[0],
                element_id=row[1],
                element_parent_id=row[2],
                equipment_name=row[3],
                phase_name=row[4],
                phase_node=row[5],
                phase_no=row[6],
                phase_status=row[7],
                actual_start=row[8],
                actual_end=row[9],
                duration=row[10],
                subphases= list())

            if actual_Phase != None:
                actual_UP.phases.append(actual_Phase)

            actual_Phase = up

        if row[11] == "SubPhase" and row[2] == actual_Phase.element_id:
            sup = SubPhase(
                prid=row[0],
                element_id=row[1],
                element_parent_id=row[2],
                equipment_name=row[3],
                subphase_name=row[4],
                subphase_node=row[5],
                subphase_no=row[6],
                subphase_status=row[7],
                actual_start=row[8],
                actual_end=row[9],
                duration=row[10])

            actual_Phase.subphases.append(sup)

    if actual_Phase != None:
        actual_UP.phases.append(actual_Phase)

    if actual_UP != None:
        batch.unit_procedures.append(actual_UP)

    cursor.close()

def get_areas():
    cursor = conn.cursor()
    sqlcmd = """SELECT area.[AREA_ID]
                      ,ISNULL(t1.LANGUAGE_TEXT, area.NAME) AS Area
                    FROM [IFACE].[dbo].[AREA]
                        LEFT JOIN LANGUAGE_TEXT t1
                            ON area.NAME = t1.Reference_Text
                                AND t1.Language = 'EN'
                    ORDER BY ISNULL(t1.LANGUAGE_TEXT, area.NAME)"""

    cursor.execute(sqlcmd)

    area_list = list()

    for area in cursor:
        ar = Area (
            area_id=area[0],
            area=area[1])

        area_list.append(ar)

    cursor.close()
    return area_list

def get_products():
    cursor = conn.cursor()
    sqlcmd = """SELECT DISTINCT ISNULL(t1.LANGUAGE_TEXT, PRODUCT) AS Product
                    FROM BATCH ba
                        LEFT JOIN LANGUAGE_TEXT t1
                            ON ba.Product = t1.Reference_Text
                                AND t1.Language = 'EN'
                    ORDER BY ISNULL(t1.LANGUAGE_TEXT, PRODUCT)"""

    cursor.execute(sqlcmd)

    product_list = list()

    for product in cursor:
        product_list.append(product[0])

    cursor.close()
    return product_list

def get_parameters(prid: int):
    cursor = conn.cursor()
    sqlcmd = """SELECT pa.ELEMENT_ID
                    ,ISNULL(t1.LANGUAGE_TEXT, PARAM_NAME) AS PARAM_NAME
                    ,CASE WHEN pa.DATA_TYPE = 'string' THEN ISNULL(t2.LANGUAGE_TEXT, PRESET_VALUE_RECIPE) 
                        ELSE PRESET_VALUE_RECIPE
                        END AS PRESET_VALUE_RECIPE
                    ,CASE WHEN pa.DATA_TYPE = 'string' THEN ISNULL(t3.LANGUAGE_TEXT, PRESET_VALUE_BATCH) 
                        ELSE PRESET_VALUE_BATCH
                        END AS PRESET_VALUE_BATCH
                    ,CASE WHEN pa.DATA_TYPE = 'string' THEN ISNULL(t4.LANGUAGE_TEXT, ACTUAL_VALUE) 
                        ELSE ACTUAL_VALUE
                        END AS ACTUAL_VALUE
                    ,ISNULL(t5.LANGUAGE_TEXT, UOM) AS UOM            
                FROM BATCH_ELEMENT_PARAM pa
                    LEFT JOIN LANGUAGE_TEXT t1
                        ON pa.PARAM_NAME = t1.Reference_Text
                            AND t1.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t2
                        ON pa.PRESET_VALUE_RECIPE = t2.Reference_Text
                            AND t2.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t3
                        ON pa.PRESET_VALUE_BATCH = t3.Reference_Text
                            AND t3.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t4
                        ON pa.ACTUAL_VALUE = t4.Reference_Text
                            AND t4.Language = 'EN'
                    LEFT JOIN LANGUAGE_TEXT t5
                        ON pa.UOM = t5.Reference_Text
                            AND t5.Language = 'EN'
                WHERE pa.Prid = %s
                ORDER BY pa.Prid, pa.ELEMENT_ID"""

    cursor.execute(sqlcmd, prid)

    param_list = list()
    actual_element_id = -1
    actual_elem_param_list = list()

    for param in cursor:
        pa = Parameter(
            element_id= param[0],
            parameter_name= param[1],
            preset_val_recipe= param[2],
            preset_val_batch= param[3],
            actual_val= param[4],
            uom= param[5])

        if pa.element_id == actual_element_id:
            actual_elem_param_list.append(pa)
        else:
            if len(actual_elem_param_list) > 0:
                param_list.append(actual_elem_param_list)
                actual_elem_param_list = list()

            actual_element_id = pa.element_id
            actual_elem_param_list.append(pa)

    if len(actual_elem_param_list) > 0:
        param_list.append(actual_elem_param_list)

    cursor.close()
    return param_list