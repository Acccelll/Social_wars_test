package
{
    import flash.display.Sprite;
    import com.socialpoint.astar.recovered.AStarRecovered;
    import com.socialpoint.astar.recovered.NodesPathRecovered;
    import com.socialpoint.astar.recovered.IsoUnitRouteBridge;

    /**
     * SWF executavel usado para verificar contratos basicos da porta A*.
     * NAO e uma copia recompilada do Social Wars original.
     *
     * Saida capturada por Ruffle.traceObserver no teste Chromium:
     *   SWTEST:<caso>:PASS
     *   SWTEST:<caso>:FAIL
     *   SWTEST:SUMMARY pass=N fail=N
     */
    public class AS3Probe extends Sprite
    {
        private var passed:int = 0;
        private var failed:int = 0;

        public function AS3Probe()
        {
            trace("SWTEST:BOOT");
            try
            {
                runTests();
            }
            catch (error:Error)
            {
                failed++;
                trace("SWTEST:uncaught_exception:FAIL " +
                      error.name + " " + error.message);
            }
            trace("SWTEST:SUMMARY pass=" + passed + " fail=" + failed);
        }

        private function check(name:String, condition:Boolean):void
        {
            if (condition)
            {
                passed++;
                trace("SWTEST:" + name + ":PASS");
            }
            else
            {
                failed++;
                trace("SWTEST:" + name + ":FAIL");
            }
        }

        private function grid():AStarRecovered
        {
            var a:AStarRecovered = new AStarRecovered(8,8,[1],[2]);
            for (var y:uint=0; y<8; y++)
                for (var x:uint=0; x<8; x++)
                    a.setTerrain(x,y,1);
            return a;
        }

        private function testUnit():Object
        {
            return {flying:false, aNodes:null, myMove:[0,0],
                    bMoving:false};
        }

        private function runTests():void
        {
            var a:AStarRecovered = grid();
            var unit:Object = testUnit();
            a.findPath(0,0,1,0,unit);
            var route:NodesPathRecovered = a.walkPath;
            check("adjacent_route",route != null && route.length == 1);
            check("proxy_index",route != null && route.length > 0 &&
                  route[0].x == 1 && route[0].y == 0);

            var applied:Boolean = IsoUnitRouteBridge.applyRoute(
                unit,route,1,0,tileToPixel,false,true);
            check("bridge_pixel_target",applied &&
                  Number(unit.myMove[0]) == 64 &&
                  Number(unit.myMove[1]) == 0 &&
                  unit.bMoving === true);
            check("bridge_splice_and_append",route.length == 1 &&
                  route[0].x == 1 && route[0].y == 0);

            var ai:Object = testUnit();
            a = grid();
            a.findPath(0,0,1,1,ai);
            route = a.walkPath;
            applied = IsoUnitRouteBridge.applyRoute(
                ai,route,1,1,tileToPixel,true,true);
            check("ai_flag",applied && route.isAI === true);

            a = grid();
            a.setOccupied(2,0,true);
            a.findPath(0,0,2,0,testUnit());
            check("blocked_destination",a.walkPath.length == 0);

            a = grid();
            a.findPath(0,0,6,6,testUnit());
            route = a.walkPath;
            trace("SWTEST:LONG_PATH_LENGTH=" + route.length);
            check("long_path",route.length > 0);

            route = new NodesPathRecovered();
            route.push({x:3,y:4});
            var tile:Object = IsoUnitRouteBridge.popNextTile(route);
            check("proxy_pop",tile != null &&
                  tile.x == 3 && tile.y == 4 && route.length == 0);
        }

        private function tileToPixel(x:int,y:int):Object
        {
            // Escala ficticia do probe; NAO e a projecao real do cliente.
            return {x:Number(x)*64,y:Number(y)*32};
        }
    }
}
