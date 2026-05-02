selectedObjects = getCurrentSelection()

if selectedObjects.count == 0 then
(
    format "ERROR: No objects selected.\n"
)
else
(
    for obj in selectedObjects do
    (
        CenterPivot obj
    )
    format "SUCCESS: Pivot reset for % objects.\n" selectedObjects.count
)