package com.socialpoint.astar.recovered
{
    /**
     * Tipo de no experimental, baseado nos campos IsoNode do cliente.
     * O construtor original nao inicializa f/g/h: Number padrao = NaN.
     * Nao substitui o tipo nominal original com.socialpoint.astar.IsoNode.
     */
    public class IsoNodeRecovered
    {
        public var f:Number = NaN;
        public var g:Number = NaN;
        public var h:Number = NaN;
        public var parentNode:IsoNodeRecovered = null;
        public var xPos:uint;
        public var yPos:uint;
        public var terrain:int;
        public var occupied:Boolean = false;

        public function IsoNodeRecovered(x:uint, y:uint, terrainCode:int)
        {
            xPos = x;
            yPos = y;
            terrain = terrainCode;
        }
    }
}
