package com.socialpoint.astar.recovered
{
    import flash.utils.Proxy;
    import flash.utils.flash_proxy;

    /**
     * Porta experimental do contrato NodesPath original:
     * flash.utils.Proxy delegando a um Array.
     * Permite acesso route[0], push, splice, length e isAI.
     * NAO e compatibilidade nominal com com.socialpoint.astar.NodesPath.
     */
    public dynamic class NodesPathRecovered extends Proxy
    {
        private var _array:Array = [];
        private var _isAI:Boolean = false;

        public function NodesPathRecovered()
        {
            super();
        }

        override flash_proxy function getProperty(name:*):*
        {
            return _array[name];
        }

        override flash_proxy function setProperty(name:*, value:*):void
        {
            _array[name] = value;
        }

        override flash_proxy function callProperty(name:*, ...args):*
        {
            var method:Function = _array[name] as Function;
            return method != null ? method.apply(_array, args) : undefined;
        }

        public function push(value:*):void { _array.push(value); }
        public function shift():* { return _array.shift(); }
        public function unshift(value:*):void { _array.unshift(value); }
        public function splice(start:int, removeCount:uint):Array
        {
            return _array.splice(start, removeCount);
        }

        public function get length():uint { return _array.length; }
        public function set length(value:uint):void { _array.length = value; }
        public function get isAI():Boolean { return _isAI; }
        public function set isAI(value:Boolean):void { _isAI = value; }

        // Inspecao no prototipo: nao existe com este nome no tipo original.
        public function get points():Array { return _array; }
    }
}
