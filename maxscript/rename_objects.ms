-- rename_objects.ms
-- Renames all selected objects to SM_Object_001 format
-- Author: LAZARUS-inq
-- Part of TA learning journey

selectionList = getCurrentSelection()

if selectionList.count == 0 then
(
    format "ERROR: No objects selected.\n"
)
else
(
    counter = 1
    for obj in selectionList do
    (
        local numStr = counter as string
        while numStr.count < 3 do numStr = "0" + numStr
        obj.name = "SM_Object_" + numStr
        counter += 1
    )
    format "SUCCESS: Renamed % objects.\n" selectionList.count
)
