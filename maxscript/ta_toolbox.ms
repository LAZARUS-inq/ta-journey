-- ta_toolbox.ms
-- Dockable 3ds Max toolbox for the TA Journey pipeline scripts.
-- Scripting → Run Script → ta_toolbox.ms
-- Author: LAZARUS-inq

try (destroyDialog TAJourneyToolbox) catch ()

rollout TAJourneyToolbox "TA Journey Toolbox" width:260
(
    group "Naming"
    (
        button btnRename "Rename selected → SM_*" width:220
    )
    group "Pivot"
    (
        button btnPivot "Reset pivot (bbox center)" width:220
        label lblPivotHint "Export origin check is in Validate." align:#left
    )
    group "Validate / Export"
    (
        button btnValidateDry "Validate meshes (dry run)" width:220
        button btnValidateFix "Validate meshes (FIX)" width:220
        button btnExport "Batch export FBX…" width:220
    )

    fn toolboxDir =
    (
        local src = getThisScriptFilename()
        if src == undefined or src == "" then src = getSourceFileName()
        getFilenamePath src
    )

    fn runNeighbor name =
    (
        local path = (toolboxDir()) + name
        if doesFileExist path then
        (
            fileIn path
        )
        else
        (
            messageBox ("Missing script:\n" + path) title:"TA Journey"
        )
    )

    fn runValidator mode =
    (
        local path = (toolboxDir()) + "mesh_validator.ms"
        if not doesFileExist path then
        (
            messageBox ("Missing script:\n" + path) title:"TA Journey"
            return()
        )
        global TA_VALIDATOR_AUTORUN = false
        fileIn path
        global MODE = mode
        runValidator()
        global TA_VALIDATOR_AUTORUN = true
    )

    on btnRename pressed do runNeighbor "rename_objects.ms"
    on btnPivot pressed do runNeighbor "reset_pivot.ms"
    on btnValidateDry pressed do runValidator "dry"
    on btnValidateFix pressed do
    (
        if queryBox "Fix mode will rename, move pivots to origin, and ResetXForm + collapse.\nContinue?" title:"TA Journey" then
            runValidator "fix"
    )
    on btnExport pressed do runNeighbor "batch_export.ms"
)

createDialog TAJourneyToolbox
