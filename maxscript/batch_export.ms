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
    exportFolder = getSavePath caption:"Select FBX export folder"
    if exportFolder == undefined then
    (
        format "ERROR: Export cancelled — no folder selected.\n"
    )
    else
    (
        if exportFolder[exportFolder.count] != "\\" and exportFolder[exportFolder.count] != "/" then
            exportFolder += "\\"

        originalSelection = getCurrentSelection()
        exported = 0

        for obj in selectedObjects do
        (
            select obj
            filePath = exportFolder + obj.name + ".fbx"
            result = exportFile filePath #noPrompt selectedOnly:true using:FBXEXP
            if result then
            (
                exported += 1
                format "Exported: %\n" filePath
            )
            else
            (
                format "FAILED: %\n" filePath
            )
        )

        select originalSelection
        format "SUCCESS: Exported % / % files to %\n" exported selectedObjects.count exportFolder
    )
)
