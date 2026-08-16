-- rename_objects.ms
-- Renames selected objects to SM_<BaseName>_001 format, keeping the original name
-- Author: LAZARUS-inq
-- Part of TA learning journey

fn stripKnownPrefix name =
(
    local prefixes = #("SM_", "SK_", "ENV_")
    for p in prefixes do
    (
        if matchPattern name pattern:(p + "*") then
        (
            return substring name (p.count + 1) (name.count - p.count)
        )
    )
    name
)

fn pad3 n =
(
    local numStr = n as string
    while numStr.count < 3 do numStr = "0" + numStr
    numStr
)

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
        local baseName = stripKnownPrefix obj.name
        obj.name = "SM_" + baseName + "_" + (pad3 counter)
        counter += 1
    )
    format "SUCCESS: Renamed % objects.\n" selectionList.count
)
