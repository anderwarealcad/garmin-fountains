import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;
import Toybox.System;


class fountainsApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
        System.println("fountainsApp onStart");
    }

    // onStop() is called when your application is exiting
    function onStop(state as Dictionary?) as Void {
        System.println("fountainsApp onStop");
    }

    //! Return the initial view of your application here
    function getInitialView() as [Views] or [Views, InputDelegates] {
        return [ new fountainsView() ];
    }


}

function getApp() as fountainsApp {
    return Application.getApp() as fountainsApp;
}