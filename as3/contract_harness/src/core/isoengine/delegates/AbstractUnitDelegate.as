package core.isoengine.delegates
{
    /** Observer double for onMoveStart. Not the original gameplay class. */
    public class AbstractUnitDelegate
    {
        public var moveStarts:int = 0;
        public var lastIsAI:Boolean = false;
        public function AbstractUnitDelegate() {}
        public function onMoveStart(isAI:Boolean):void
        {
            moveStarts++;
            lastIsAI = isAI;
        }
    }
}
