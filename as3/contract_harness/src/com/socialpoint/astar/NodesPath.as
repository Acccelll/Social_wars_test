package com.socialpoint.astar
{
    import flash.utils.Proxy;
    import flash.utils.flash_proxy;

    /**
     * CONTRACT TEST DOUBLE ONLY.
     * Nominal package/type matches the recovered SWF signature but this
     * implementation is NOT the original class and must never be linked
     * into a modified Social Wars client alongside the real NodesPath.
     */
    public dynamic class NodesPath extends Proxy
    {
        private var _array:Array = [];
        private var _isAI:Boolean = false;

        public function NodesPath() { super(); }

        override flash_proxy function getProperty(name:*):* {
            return _array[name];
        }
        override flash_proxy function setProperty(name:*, value:*):void {
            _array[name] = value;
        }
        override flash_proxy function callProperty(name:*, ...args):* {
            var fn:Function = _array[name] as Function;
            return fn.apply(_array,args);
        }

        public function push(value:*):void { _array.push(value); }
        public function shift():* { return _array.shift(); }
        public function unshift(value:*):void { _array.unshift(value); }
        public function splice(start:int, removeCount:uint):Array {
            return _array.splice(start,removeCount);
        }
        public function get length():uint { return _array.length; }
        public function get isAI():Boolean { return _isAI; }
        public function set isAI(value:Boolean):void { _isAI=value; }
    }
}
