package com.socialpoint.astar
{
    import com.socialpoint.astar.recovered.NodesPathRecovered;

    /**
     * Explicit copy across the recovered-vs-original nominal type boundary.
     * Uses the contract test double in this SWF. Production integration
     * must use the real original NodesPath class, never this double.
     */
    public class RecoveredRouteAdapter
    {
        public static function copy(route:NodesPathRecovered):NodesPath
        {
            var target:NodesPath = new NodesPath();
            if (route == null) return target;
            target.isAI = route.isAI; // IMPORTANT: before IsoUnit assignment
            for (var i:uint=0; i<route.length; i++)
            {
                var point:Object = route[i] as Object;
                if (point != null) target.push({x:point.x,y:point.y});
            }
            return target;
        }
    }
}
