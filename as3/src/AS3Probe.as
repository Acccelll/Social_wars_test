package
{
    import flash.display.Sprite;
    import com.socialpoint.astar.recovered.AStarRecovered;
    import com.socialpoint.astar.recovered.NodesPathRecovered;
    import com.socialpoint.astar.recovered.IsoUnitRouteBridge;

    /** Ponto de entrada de compilacao experimental (nao o jogo). */
    public class AS3Probe extends Sprite
    {
        public function AS3Probe()
        {
            var astar:AStarRecovered =
                new AStarRecovered(8,8,[1],[2]);
            for (var y:int=0; y<8; y++)
                for (var x:int=0; x<8; x++)
                    astar.setTerrain(uint(x),uint(y),1);

            var unit:Object = {
                flying:false, aNodes:null, myMove:[0,0], bMoving:false
            };
            astar.findPath(0,0,6,6,unit);
            var route:NodesPathRecovered = astar.walkPath;
            trace("Path nodes: " + route.length);
            if (route.length > 0)
            {
                trace("First tile: " + route[0].x + "," + route[0].y);
                var ok:Boolean = IsoUnitRouteBridge.applyRoute(
                    unit,route,6,6,tileToPixel,false,true);
                trace("Route bridge result: " + ok);
            }
        }

        private function tileToPixel(x:int,y:int):Object
        {
            // ESCALA FICTICIA APENAS PARA O PROBE.
            return {x:Number(x)*64,y:Number(y)*32};
        }
    }
}
