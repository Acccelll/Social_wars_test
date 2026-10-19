package
{
    import flash.display.Sprite;
    import flash.external.ExternalInterface;
    import flash.utils.getQualifiedClassName;
    import com.socialpoint.astar.NodesPath;
    import com.socialpoint.astar.RecoveredRouteAdapter;
    import com.socialpoint.astar.recovered.NodesPathRecovered;
    import core.isoengine.IsoUnit;
    import core.isoengine.delegates.AbstractUnitDelegate;

    /**
     * Ruffle runtime test of typed compatibility contracts ONLY.
     * IsoUnit, NodesPath, AbstractUnitDelegate here are test doubles.
     */
    public class ContractProbe extends Sprite
    {
        private var pass:int = 0;
        private var fail:int = 0;

        public function ContractProbe()
        {
            send("SWTEST:BOOT");
            try { cases(); }
            catch (e:Error)
            {
                fail++;
                send("SWTEST:uncaught_exception:FAIL " + e.message);
            }
            send("SWTEST:SUMMARY pass="+pass+" fail="+fail);
        }

        private function send(s:String):void
        {
            trace(s);
            try {
                if (ExternalInterface.available)
                    ExternalInterface.call("swProbeSignal",s);
            } catch(e:Error) {}
        }
        private function check(k:String, condition:Boolean):void
        {
            if (condition) { pass++; send("SWTEST:"+k+":PASS"); }
            else { fail++; send("SWTEST:"+k+":FAIL"); }
        }

        private function cases():void
        {
            var observer:AbstractUnitDelegate = new AbstractUnitDelegate();
            var unit:IsoUnit = new IsoUnit(observer);

            var empty:NodesPath = new NodesPath();
            unit.aNodes = empty;
            check("empty_no_event",observer.moveStarts == 0);
            check("typed_setter_getter",unit.aNodes === empty);
            check("nominal_type",getQualifiedClassName(unit.aNodes) ==
                  "com.socialpoint.astar::NodesPath");

            var manual:NodesPath = new NodesPath();
            manual.push({x:3,y:4});
            unit.aNodes = manual;
            check("manual_event",observer.moveStarts == 1 &&
                  observer.lastIsAI == false);
            check("proxy_index",unit.aNodes[0].x == 3 &&
                  unit.aNodes[0].y == 4);

            manual.isAI = true;
            check("no_event_on_flag_mutation",observer.moveStarts == 1);
            unit.aNodes = manual;
            check("reassignment_uses_isAI",observer.moveStarts == 2 &&
                  observer.lastIsAI == true);

            manual.splice(0,1);
            check("splice_removes_tile",manual.length == 0);
            unit.aNodes = manual;
            check("cleared_route_no_event",observer.moveStarts == 2);

            manual.unshift({x:5,y:6});
            var tile:Object = manual.shift() as Object;
            check("proxy_shift_unshift",manual.length == 0 &&
                  tile.x == 5 && tile.y == 6);

            var recovered:NodesPathRecovered = new NodesPathRecovered();
            recovered.isAI = true;
            recovered.push({x:7,y:2});
            var converted:NodesPath = RecoveredRouteAdapter.copy(recovered);
            check("adapter_copies_coordinates",converted.length == 1 &&
                  converted[0].x == 7 && converted[0].y == 2);
            check("adapter_preserves_isAI",converted.isAI === true);
            unit.aNodes = converted;
            check("adapter_assignment_ai_event",observer.moveStarts == 3 &&
                  observer.lastIsAI == true);

            recovered[0] = {x:1,y:1};
            check("adapter_is_independent_copy",converted[0].x == 7 &&
                  converted[0].y == 2);

            unit.aNodes = null;
            check("nullable_setter",unit.aNodes == null &&
                  observer.moveStarts == 3);
        }
    }
}
