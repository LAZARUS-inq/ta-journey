-- reset_pivot.ms
-- Resets pivot to bounding box center for all selected objects
-- Author: LAZARUS-inq
-- Part of TA learning journey

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
