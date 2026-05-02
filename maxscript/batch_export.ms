-- batch_export.ms
-- Exports each selected object as a separate FBX file
-- Author: LAZARUS-inq
-- Part of TA learning journey

selectedObjects = getCurrentSelection()

if selectedObjects.count == 0 then
(
    format "ERROR: No objects selected.\n"
)
else
(
    exportFolder = "C:\\Exports\\"
    if not doesFileExist exportFolder then makeDir exportFolder

    originalSelection = getCurrentSelection()

    for obj in selectedObjects do
    (
        select obj
        filePath = exportFolder + obj.name + ".fbx"
        exportFile filePath #noPrompt selectedOnly:true using:FBXEXP
    )

    select originalSelection
    format "SUCCESS: Exported % files to %\n" selectedObjects.count exportFolder
)