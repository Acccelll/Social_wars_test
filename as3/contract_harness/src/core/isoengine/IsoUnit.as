package core.isoengine
{
    import com.socialpoint.astar.NodesPath;
    import core.isoengine.delegates.AbstractUnitDelegate;

    /**
     * Contract double of original IsoUnit.aNodes get/set signatures.
     * Original SWF setter ABC method #1788:
     * store NodesPath, then onMoveStart(route.isAI) only if length > 0.
     * No original rendering or movement logic is included.
     */
    public class IsoUnit
    {
        private var _aNodes:NodesPath;
        public var delegate:AbstractUnitDelegate;

        public function IsoUnit(observer:AbstractUnitDelegate)
        {
            delegate = observer;
        }
        public function get aNodes():NodesPath
        {
            return _aNodes;
        }
        public function set aNodes(value:NodesPath):void
        {
            _aNodes = value;
            if (_aNodes != null && _aNodes.length > 0 && delegate != null)
                delegate.onMoveStart(_aNodes.isAI);
        }
    }
}
