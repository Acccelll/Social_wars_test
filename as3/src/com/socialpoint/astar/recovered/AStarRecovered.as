package com.socialpoint.astar.recovered
{
    import flash.utils.Dictionary;
    import flash.utils.getTimer;

    /**
     * Port independente e EXPERIMENTAL das rotinas AStar.
     *
     * Referencia: Basesec_1.5.4.swf, ABC 543/551/552/553/554/555/558.
     * NAO e substituicao drop-in do SWF: usa tipos Recovered e callbacks
     * para recursos que dependem de core.Base/Config/Constants.
     *
     * Regra g literal observada no AVM2:
     *   Boolean(current.g + Number(diagonal)) ? 14 : 10
     * (NAO usa custo acumulado convencional).
     */
    public class AStarRecovered
    {
        public static const CANCEL_TIME:int = 50;

        private var xDepth:uint;
        private var yDepth:uint;
        private var mNodes:Array;
        private var defaultTerrains:Dictionary = new Dictionary();
        private var waterTerrains:Dictionary = new Dictionary();
        private var startNode:IsoNodeRecovered;
        private var destNode:IsoNodeRecovered;
        private var dOpen:Dictionary = new Dictionary();
        private var aOpen:Array = [];
        private var dClosed:Dictionary = new Dictionary();
        private var path:NodesPathRecovered = new NodesPathRecovered();
        private var dBannedUnits:Dictionary = new Dictionary();
        private var uUnit:Object;
        private var _iDuration:int;

        public var paintedNodes:Array = [];
        // Callback function(unit:Object):Boolean
        public var isWaterborne:Function;
        // Callback function(sx:uint,sy:uint,dx:uint,dy:uint):*
        public var flightLineProvider:Function;

        public function AStarRecovered(
            width:uint, height:uint,
            landCodes:Array = null, waterCodes:Array = null)
        {
            xDepth = width;
            yDepth = height;
            setAllowedTerrains(landCodes, waterCodes);
            initNodes();
        }

        public function setAllowedTerrains(land:Array, water:Array):void
        {
            defaultTerrains = new Dictionary();
            waterTerrains = new Dictionary();
            var code:*;
            if (land != null)
                for each (code in land) defaultTerrains[int(code)] = true;
            if (water != null)
                for each (code in water) waterTerrains[int(code)] = true;
        }

        public function initNodes():void
        {
            mNodes = [];
            for (var y:uint = 0; y < yDepth; y++)
            {
                var row:Array = [];
                for (var x:uint = 0; x < xDepth; x++)
                    row.push(new IsoNodeRecovered(x, y, 0));
                mNodes.push(row);
            }
        }

        public function getNode(x:uint, y:uint):IsoNodeRecovered
        {
            if (x >= xDepth || y >= yDepth) return null;
            return mNodes[y][x] as IsoNodeRecovered;
        }

        public function setTerrain(x:uint, y:uint, terrain:int):void
        {
            var n:IsoNodeRecovered = getNode(x, y);
            if (n != null) n.terrain = terrain;
        }

        public function setOccupied(x:uint, y:uint, value:Boolean):void
        {
            var n:IsoNodeRecovered = getNode(x, y);
            if (n != null) n.occupied = value;
        }

        public function getTerrain(x:int, y:int):int
        {
            if (x < 0 || y < 0 || x >= xDepth || y >= yDepth) return -1;
            return mNodes[y][x].terrain;
        }

        public function isWalkable(
            x:int, y:int, allowed:Dictionary = null):Boolean
        {
            if (allowed == null) allowed = defaultTerrains;
            if (x < 0 || y < 0 || x >= xDepth || y >= yDepth) return false;
            var n:IsoNodeRecovered = mNodes[y][x] as IsoNodeRecovered;
            return n != null && !n.occupied && Boolean(allowed[n.terrain]);
        }

        public function get walkPath():NodesPathRecovered { return path; }

        public function canFindPath(
            sx:uint, sy:uint, ex:uint, ey:uint):Boolean
        {
            // Aproximacao: sem pintarMapa() original, assume conectado.
            if (paintedNodes == null || paintedNodes.length == 0)
                return true;
            return paintedNodes[sy * 100 + sx] ==
                   paintedNodes[ey * 100 + ex];
        }

        public function findPath(
            sx:uint, sy:uint, ex:uint, ey:uint,
            unit:Object, ignoreBan:Boolean = false):void
        {
            var allowed:Dictionary = defaultTerrains;
            if (isWaterborne != null && isWaterborne(unit))
                allowed = waterTerrains;

            _iDuration = getTimer() + CANCEL_TIME;
            path = new NodesPathRecovered();
            dOpen = new Dictionary();
            aOpen = [];
            dClosed = new Dictionary();

            if (sx >= xDepth || ex >= xDepth ||
                sy >= yDepth || ey >= yDepth) return;

            if (unit != null && Boolean(unit["flying"]))
            {
                if (sx == ex && sy == ey)
                    path.push({x:ex, y:ey});
                else if (flightLineProvider != null)
                {
                    var flight:* = flightLineProvider(sx, sy, ex, ey);
                    if (flight is NodesPathRecovered)
                        path = flight as NodesPathRecovered;
                    else if (flight is Array)
                        for each (var p:Object in flight) path.push(p);
                }
                return;
            }

            if (!canFindPath(sx,sy,ex,ey)) return;

            if (!ignoreBan && unit != null &&
                dBannedUnits[unit] != null)
            {
                if (getTimer() > Number(dBannedUnits[unit]))
                    delete dBannedUnits[unit];
                else
                    return;
            }

            uUnit = unit;
            startNode = getNode(sx,sy);
            destNode = getNode(ex,ey);
            if (startNode == null || destNode == null ||
                !isWalkable(sx,sy,allowed) ||
                !isWalkable(ex,ey,allowed)) return;

            if ((sx == ex && sy == ey) ||
                (sx == ex && Math.abs(int(sy)-int(ey)) == 1) ||
                (sy == ey && Math.abs(int(sx)-int(ex)) == 1))
            {
                path.unshift({x:ex,y:ey});
                return;
            }

            look(startNode, allowed);
        }

        private function Sort():void
        {
            aOpen.sortOn("f", Array.NUMERIC);
        }

        private function searchNode(
            candidate:IsoNodeRecovered,
            current:IsoNodeRecovered, allowed:Dictionary):void
        {
            if (candidate == null) return;
            var diagonal:Boolean =
                candidate.xPos != current.xPos &&
                candidate.yPos != current.yPos;

            var blockedCorner:Boolean = false;
            if (diagonal)
            {
                var dx:int = int(candidate.xPos)-int(current.xPos);
                var dy:int = int(candidate.yPos)-int(current.yPos);
                var horizontal:IsoNodeRecovered = getNode(
                    uint(int(current.xPos)+dx),current.yPos);
                var vertical:IsoNodeRecovered = getNode(
                    current.xPos,uint(int(current.yPos)+dy));
                blockedCorner =
                    horizontal == null || vertical == null ||
                    !isWalkable(int(horizontal.xPos),int(horizontal.yPos),allowed) ||
                    !isWalkable(int(vertical.xPos),int(vertical.yPos),allowed);
            }

            if (candidate.occupied || blockedCorner ||
                !Boolean(allowed[candidate.terrain]) ||
                dClosed[candidate] === true) return;

            // Transcricao semantica do AVM2, NAO A* acumulativo.
            var nextG:Number =
                Boolean(current.g + Number(diagonal)) ? 14 : 10;

            if (dOpen[candidate] !== true)
            {
                candidate.parentNode = current;
                candidate.g = nextG;
                candidate.h = 10 * (
                    Math.abs(int(destNode.xPos)-int(candidate.xPos)) +
                    Math.abs(int(destNode.yPos)-int(candidate.yPos)));
                candidate.f = candidate.g + candidate.h;
                aOpen.push(candidate);
                dOpen[candidate] = true;
            }
            else if (nextG < candidate.g)
            {
                candidate.g = nextG;
                candidate.parentNode = current;
                // O ramo original nao recalcula f aqui.
            }
        }

        private function ResolvePath(last:IsoNodeRecovered):void
        {
            if (last.parentNode == startNode)
            {
                path.unshift({x:last.xPos,y:last.yPos});
                return;
            }
            // Reconstrucao de confianca MEDIA: o destino e tratado
            // de modo diferente dos nos intermediarios.
            var p:IsoNodeRecovered = last;
            while (p != null && p != startNode)
            {
                if (p != destNode)
                    path.unshift({x:p.xPos,y:p.yPos});
                p = p.parentNode;
            }
        }

        private function look(start:IsoNodeRecovered, allowed:Dictionary):void
        {
            var current:IsoNodeRecovered = start;
            var iterations:int = 0;

            while (current != null)
            {
                iterations++;
                if (iterations % 100 == 0)
                {
                    var now:int = getTimer();
                    if (now > _iDuration)
                    {
                        path = new NodesPathRecovered();
                        if (uUnit != null)
                            dBannedUnits[uUnit] =
                                now + int(1000 + Math.random()*2000);
                        return;
                    }
                }

                dClosed[current] = true;
                if (current == destNode)
                {
                    ResolvePath(current);
                    return;
                }

                var ymin:int = int(Math.max(current.yPos-1,0));
                var ymax:int = int(Math.min(current.yPos+1,yDepth-1));
                var xmin:int = int(Math.max(current.xPos-1,0));
                var xmax:int = int(Math.min(current.xPos+1,xDepth-1));

                for (var y:int = ymin; y <= ymax; y++)
                {
                    for (var x:int = xmin; x <= xmax; x++)
                    {
                        if (x == int(current.xPos) &&
                            y == int(current.yPos)) continue;
                        searchNode(getNode(uint(x),uint(y)),current,allowed);
                    }
                }

                Sort();
                delete dOpen[current];
                var next:Array = aOpen.splice(0,1);
                current = next.length ?
                    next[0] as IsoNodeRecovered : null;
            }
        }
    }
}
