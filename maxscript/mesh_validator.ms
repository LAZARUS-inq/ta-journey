-- ================================================================================
--   mesh_validator.ms — 3ds Max Mesh Validator
-- ================================================================================
--   Author  : LAZARUS-inq
--   GitHub  : https://github.com/LAZARUS-inq
--   Version : 2.0.0
--
--   HOW TO RUN
--   ----------
--   Inside 3ds Max:
--     Scripting -> Run Script -> select this file
--
--   DESCRIPTION
--   -----------
--   A pre-export validation tool that checks all selected meshes (or scene
--   meshes) against common pipeline requirements before FBX export to UE5.
--   Supports two modes: Dry Run (report only) and Fix Mode (auto-fix issues).
--
--   CHECKS PERFORMED
--   ----------------
--   - Naming convention   : mesh name must start with SM_
--   - Pivot position      : pivot must be at world origin
--   - Scale               : XYZ scale must be (1, 1, 1)
--   - UV Channel 0        : must have at least one UV channel
--   - Modifiers           : warns about leftover modifiers (Edit Poly etc.)
--   - Polycount           : warns if triangle count exceeds MAX_TRIS limit
--
--   SETTINGS
--   --------
--   MODE            "dry"  = report only, no changes made.
--                   "fix"  = auto-fix naming, pivot and scale issues.
--   MAX_TRIS        Maximum allowed triangle count before warning.
--   CHECK_SELECTED  True = validate selected objects only.
--                   False = validate all meshes in scene.
--   LOG_PATH        Folder where the TXT report will be saved.
-- ================================================================================

-- ─── Settings ──────────────────────────────────────────────────────────────────
global MODE           = "fix"      -- "dry" = report only | "fix" = auto-fix
global MAX_TRIS       = 50000
global CHECK_SELECTED = true
global LOG_PATH       = "C:/UE5_Reports/"

-- ─── Logging ───────────────────────────────────────────────────────────────────
global validationLog = #()

fn logMsg msg = (
    append validationLog msg
    format "%\n" msg
)

-- ─── Fix: Naming ───────────────────────────────────────────────────────────────
fn fixNaming obj = (
    local oldName = obj.name
    local newName = "SM_" + oldName
    obj.name = newName
    logMsg ("  [FIXED] Naming: '" + oldName + "' -> '" + newName + "'")
)

-- ─── Fix: Pivot ────────────────────────────────────────────────────────────────
fn fixPivot obj = (
    local bbMin = obj.min
    local bbMax = obj.max
    local center = (bbMin + bbMax) / 2.0
    obj.pivot = center
    logMsg ("  [FIXED] Pivot: moved to bounding box center (" + (center.x as string) + ", " + (center.y as string) + ", " + (center.z as string) + ")")
)

-- ─── Fix: Scale ────────────────────────────────────────────────────────────────
fn fixScale obj = (
    ResetXForm obj
    collapseStack obj
    logMsg ("  [FIXED] Scale: ResetXForm applied and stack collapsed")
)

-- ─── Check: Naming Convention ──────────────────────────────────────────────────
fn checkNaming obj = (
    local name = obj.name
    if (matchPattern name pattern:"SM_*") then (
        logMsg ("  [OK] Naming: " + name)
        return true
    ) else (
        if MODE == "fix" then (
            fixNaming obj
            return true
        ) else (
            logMsg ("  [FAIL] Naming: '" + name + "' — must start with SM_")
            return false
        )
    )
)

-- ─── Check: Scale ──────────────────────────────────────────────────────────────
fn checkScale obj = (
    local s = obj.scale
    local ok = (abs(s.x - 1.0) < 0.001) and (abs(s.y - 1.0) < 0.001) and (abs(s.z - 1.0) < 0.001)
    if ok then (
        logMsg ("  [OK] Scale: (1, 1, 1)")
        return true
    ) else (
        if MODE == "fix" then (
            fixScale obj
            return true
        ) else (
            logMsg ("  [FAIL] Scale: (" + (s.x as string) + ", " + (s.y as string) + ", " + (s.z as string) + ") — must be (1, 1, 1)")
            return false
        )
    )
)

-- ─── Check: Pivot ──────────────────────────────────────────────────────────────
fn checkPivot obj = (
    local p = obj.pivot
    local atOrigin = (abs(p.x) < 0.01) and (abs(p.y) < 0.01) and (abs(p.z) < 0.01)
    if atOrigin then (
        logMsg ("  [OK] Pivot: at world origin")
        return true
    ) else (
        if MODE == "fix" then (
            fixPivot obj
            return true
        ) else (
            logMsg ("  [WARN] Pivot: (" + (p.x as string) + ", " + (p.y as string) + ", " + (p.z as string) + ") — not at origin")
            return false
        )
    )
)

-- ─── Check: UV Channel ─────────────────────────────────────────────────────────
fn checkUV obj = (
    local meshObj = snapshotAsMesh obj
    local uvCount = meshObj.numTVerts
    delete meshObj

    if uvCount > 0 then (
        logMsg ("  [OK] UV Channel 0: " + (uvCount as string) + " verts")
        return true
    ) else (
        logMsg ("  [FAIL] UV Channel 0: missing or empty — fix manually")
        return false
    )
)

-- ─── Check: Modifiers ──────────────────────────────────────────────────────────
fn checkModifiers obj = (
    local modCount = obj.modifiers.count
    if modCount == 0 then (
        logMsg ("  [OK] Modifiers: none")
        return true
    ) else (
        local modNames = ""
        for m in obj.modifiers do modNames += (m.name + " ")
        logMsg ("  [WARN] Modifiers: " + (modCount as string) + " found — [" + modNames + "] — collapse manually")
        return false
    )
)

-- ─── Check: Polycount ──────────────────────────────────────────────────────────
fn checkPolycount obj = (
    local meshObj = snapshotAsMesh obj
    local tris = meshObj.numFaces
    delete meshObj

    if tris <= MAX_TRIS then (
        logMsg ("  [OK] Polycount: " + (tris as string) + " tris")
        return true
    ) else (
        logMsg ("  [WARN] Polycount: " + (tris as string) + " tris — exceeds limit of " + (MAX_TRIS as string))
        return false
    )
)

-- ─── Validate Single Object ────────────────────────────────────────────────────
fn validateObject obj = (
    local results = #(false, false, false, false, false, false)

    logMsg ("")
    logMsg (">>> " + obj.name)

    results[1] = checkNaming    obj
    results[2] = checkScale     obj
    results[3] = checkPivot     obj
    results[4] = checkUV        obj
    results[5] = checkModifiers obj
    results[6] = checkPolycount obj

    local passed = 0
    for r in results do if r then passed += 1

    logMsg ("  Result: " + (passed as string) + "/6 checks passed")
    return results
)

-- ─── Save Report ───────────────────────────────────────────────────────────────
fn saveReport = (
    makeDir LOG_PATH

    local timestamp = (localTime as string)
    local filename  = LOG_PATH + "mesh_validator_report.txt"

    local f = openFile filename mode:"w"
    if f != undefined then (
        format "================================================================================\n" to:f
        format "  MESH VALIDATOR REPORT\n" to:f
        format "  Mode      : %\n" MODE to:f
        format "  Timestamp : %\n" timestamp to:f
        format "================================================================================\n" to:f
        for line in validationLog do format "%\n" line to:f
        close f
        logMsg ("")
        logMsg ("Report saved: " + filename)
    ) else (
        logMsg ("ERROR: Could not save report to " + filename)
    )
)

-- ─── Main ──────────────────────────────────────────────────────────────────────
fn runValidator = (
    validationLog = #()

    local objects = #()

    if CHECK_SELECTED then (
        for obj in selection do (
            if superClassOf obj == GeometryClass do append objects obj
        )
        if objects.count == 0 then (
            logMsg "No geometry selected. Set CHECK_SELECTED = false to scan entire scene."
            return()
        )
    ) else (
        for obj in geometry do append objects obj
    )

    logMsg "================================================================================"
    if MODE == "dry" then (
        logMsg "  MESH VALIDATOR — DRY RUN (no changes will be made)"
    ) else (
        logMsg "  MESH VALIDATOR — FIX MODE (issues will be auto-fixed)"
    )
    logMsg ("  Objects to check: " + (objects.count as string))
    logMsg "================================================================================"

    local totalPassed = 0
    local totalFailed = 0

    for obj in objects do (
        local results = validateObject obj
        for r in results do (
            if r then totalPassed += 1 else totalFailed += 1
        )
    )

    logMsg ""
    logMsg "================================================================================"
    logMsg "  RESULTS"
    logMsg ("  Mode            : " + MODE)
    logMsg ("  Objects checked : " + (objects.count as string))
    logMsg ("  Checks passed   : " + (totalPassed as string))
    logMsg ("  Checks failed   : " + (totalFailed as string))
    if MODE == "fix" then (
        logMsg "  Auto-fixed      : Naming, Pivot, Scale"
        logMsg "  Manual required : UV Channel, Modifiers, Polycount"
    )
    logMsg "================================================================================"

    saveReport()
)

-- ─── Run ───────────────────────────────────────────────────────────────────────
runValidator()
