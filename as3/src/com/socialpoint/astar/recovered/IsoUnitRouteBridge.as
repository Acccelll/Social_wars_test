package com.socialpoint.astar.recovered
{
    /**
     * Reproduz o contrato observavel IsoUnit.aNodes em um objeto de teste.
     * O setter original de IsoUnit exige o tipo nominal NodesPath,
     * portanto isto NAO faz um patch binario no jogo.
     */
    public class IsoUnitRouteBridge
    {
        public static function applyRoute(
            unit:Object,
            route:NodesPathRecovered,
            destX:int,
            destY:int,
            tileToPixel:Function,
            isAI:Boolean = false,
            appendDestination:Boolean = true):Boolean
        {
            if (unit == null || route == null || tileToPixel == null)
                return false;

            // A ordem isAI -> setter aNodes importa para onMoveStart.
            route.isAI = isAI;
            unit["aNodes"] = route;

            if (route.length == 0)
            {
                unit["myMove"] = [0,0];
                unit["bMoving"] = false;
                return false;
            }

            var first:Object = route[0] as Object;
            if (first == null) return false;
            var px:Object = tileToPixel(int(first["x"]),int(first["y"]));
            if (px == null) return false;

            unit["myMove"] = [Number(px["x"]),Number(px["y"])];
            route.splice(0,1);
            if (appendDestination)
                route.push({x:destX,y:destY});
            unit["bMoving"] = true;
            return true;
        }

        public static function popNextTile(
            route:NodesPathRecovered):Object
        {
            if (route == null || route.length == 0) return null;
            var result:Object = route[0] as Object;
            route.splice(0,1);
            return result;
        }
    }
}
