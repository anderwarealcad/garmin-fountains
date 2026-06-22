import Toybox.Activity;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.WatchUi;
import Toybox.System;
import Toybox.Position;
import Toybox.Math;

class fountainsView extends WatchUi.DataField {

    var version = "1.0.3";

    hidden var mValue as Numeric;
    var lat;
    var lon;
    var fountains = [] as Array<Float>;
    var dis as Float;
    var bea as Float;
    var latMajor;
    var latMinor;
    var lonMajor;
    var lonMinor;
    var latMajor_ant;
    var latMinor_ant;
    var lonMajor_ant;
    var lonMinor_ant;
    var conf = [] as Array;
    var name as String = "";
    var device as String = "";
    var screen = [] as Array;
    var screenX as Integer;
    var screenY as Integer;
    var screenShape as String = "";
    var err as String = "";
    var font;

    function initialize() {
        DataField.initialize();
        lat = 0.0;
        lon = 0.0;
        mValue = 0.0f;
        dis = 0.0;
        bea=0.0;
        latMajor=0.0;
        latMinor=0.0;
        lonMajor=0.0;
        lonMinor=0.0;
        latMajor_ant=0.0;
        latMinor_ant=0.0;
        lonMajor_ant=0.0;
        lonMinor_ant=0.0;
        try{
            conf = ConfLoader.getConfData();
        }catch(e){
            err = e.toString();
            System.println(err);
        }
        var _conf = conf as Array;
        name = _conf[2];
        device = _conf[3];
        screenX = _conf[4];
        screenY = _conf[5];
        screenShape = _conf[6];

        System.println("scr > "+ device + " " + screenX + " " + screenY + " " + screenShape);
    }

    // Set your layout here. Anytime the size of obscurity of
    // the draw context is changed this will be called.
    function onLayout(dc as Dc) as Void {

    }

    // The given info object contains all the current workout information.
    // Calculate a value and save it locally in this method.
    // Note that compute() and onUpdate() are asynchronous, and there is no
    // guarantee that compute() will be called before onUpdate().
    function compute(info as Activity.Info) as Void {
        // See Activity.Info in the documentation for available information.
        if(info has :currentHeartRate){
            if(info.currentHeartRate != null){
                mValue = info.currentHeartRate as Number;
            } else {
                mValue = 0.0f;
            }
        }

        if (info.currentLocation != null) {

            lat = info.currentLocation.toDegrees()[0];
            lon = info.currentLocation.toDegrees()[1];
            System.println("gps > " + lat.format("%.4f") + " " + lon.format("%.4f"));
    
            if(lat>=0.0){
                latMajor = Math.floor(lat);
                latMinor = Math.floor((lat - latMajor) * 10);
            }else{
                latMajor = Math.ceil(lat);
                latMinor = Math.ceil((lat - latMajor) * 10);
                latMinor = -latMinor;
            }
            if(lon>=0.0){
                lonMajor = Math.floor(lon);
                lonMinor = Math.floor((lon - lonMajor) * 10);
            }else{
                lonMajor = Math.ceil(lon);
                lonMinor = Math.ceil((lon - lonMajor) * 10);
                lonMinor = -lonMinor;
            }
            System.println("til > " + latMajor.toNumber() + " " + latMinor.toNumber() + " " + lonMajor.toNumber() + " " + lonMinor.toNumber());

            if(latMajor==latMajor_ant && latMinor==latMinor_ant && lonMajor==lonMajor_ant && lonMinor==lonMinor_ant){
                System.println("tile igual, no recargo");
        
            }else{
                System.println("tile nuevo, recargo");
                latMajor_ant=latMajor;
                latMinor_ant=latMinor;
                lonMajor_ant=lonMajor;
                lonMinor_ant=lonMinor;
                //necesitas poner la carpeta source/tiles con la correspondientes .mc tiles y el TileLoader.mc que se genera con tools/get_fountains.py
                try{
                    fountains = TileLoader.getTileData(latMajor, latMinor, lonMajor, lonMinor);
                }catch(e){
                    err = e.toString();
                    System.println(err);
                }
            }

            //var res=getNearestFountain(lat, lon, fountains as Array<Float>);
            var res=getNearestFountain_v2(lat, lon, fountains as Array<Float>);
  
            var resDict = res as Dictionary;
            dis = resDict[:distance].toFloat();
            var f_lat = resDict[:lat].toFloat();
            var f_lon = resDict[:lon].toFloat();

            //System.println("fou > " + f_lat.format("%.4f") + " " + f_lon.format("%.4f"));

            //obtener la direccion de la fuente
            bea=getBearing(lat, lon, f_lat, f_lon);
            //System.println("dir > " + bearingToText(bea));

            System.println(" ");

        }
    }

    // Display the value you computed here. This will be called
    // once a second when the data field is visible.
    function onUpdate(dc as Dc) as Void {
        // Set the background color
        var text;
    
        // Call parent's onUpdate(dc) to redraw the layout
        View.onUpdate(dc);

        dc.clear();

        if(dis<1.0){
            text = "Fuente de agua a\n " + (dis*1000.0).format("%.0f") + " m";
        }else{
            text = "Fuente de agua a\n " + dis.format("%.2f") + " km";
        }



        
        if (screenShape.equals("circle")) {
            //System.println("font xtiny");

            font = Graphics.FONT_XTINY;

            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX/2,screenY/7,font,text,Graphics.TEXT_JUSTIFY_CENTER);

            drawBearingArrow(dc, bea, screenX, screenY);

            text = lat.format("%.2f") + "," + lon.format("%.2f");
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX/2,screenY-50,font,text,Graphics.TEXT_JUSTIFY_CENTER);

            text = name + " " + version;
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX/2,screenY-80,font,text,Graphics.TEXT_JUSTIFY_CENTER);

            text = err;
            dc.setColor(Graphics.COLOR_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX/2,screenY-110,font,text,Graphics.TEXT_JUSTIFY_CENTER);

        }else if(screenShape.equals("rectangle")) {
            //System.println("font small");

            font = Graphics.FONT_SMALL;

            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX/2,screenY/7,font,text,Graphics.TEXT_JUSTIFY_CENTER);

            drawBearingArrow(dc, bea, screenX, screenY);

            text = lat.format("%.2f") + "," + lon.format("%.2f");
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(0,screenY-20,font,text,Graphics.TEXT_JUSTIFY_LEFT);

            text = err;
            dc.setColor(Graphics.COLOR_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(0,screenY-40,font,text,Graphics.TEXT_JUSTIFY_LEFT);

            text = name + " " + version;
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX-10,screenY-20,font,text,Graphics.TEXT_JUSTIFY_RIGHT);

        }else{
            //System.println("font default");
            
            font = Graphics.FONT_XTINY;

            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX/2,screenY/7,font,text,Graphics.TEXT_JUSTIFY_CENTER);

            drawBearingArrow(dc, bea, screenX, screenY);

            text = lat.format("%.2f") + "," + lon.format("%.2f");
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(0,screenY-20,font,text,Graphics.TEXT_JUSTIFY_LEFT);

            text = err;
            dc.setColor(Graphics.COLOR_RED, Graphics.COLOR_TRANSPARENT);
            dc.drawText(0,screenY-40,font,text,Graphics.TEXT_JUSTIFY_LEFT);

            text = name + " " + version;
            dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
            dc.drawText(screenX-10,screenY-20,font,text,Graphics.TEXT_JUSTIFY_RIGHT);
        }





    }

    //function getNearestFountain(currentLat, currentLon, fountains as Array<Dictionary<Symbol, Float>>) {
    function getNearestFountain(currentLat, currentLon, fountains as Array<Float>) {

        var minDistance = 999999.0;
        var nearest = null;

        for (var i = 0; i < fountains.size(); i++) {

            var f = fountains[i] as Array<Float>;
        
            var d = distanciaKm(
                currentLat,
                currentLon,
                f[0],   // lat
                f[1]    // lon
            );

            if (d < minDistance) {
                minDistance = d;
                nearest = f;
            }
        }

        return {
            :fountain => nearest,
            :distance => minDistance
        };
    }

    function getNearestFountain_v2(currentLat, currentLon, fountains as Array) {

        var minDistance = 999999.0;
        var nearestLat = 0.0;
        var nearestLon = 0.0;

        for (var i = 0; i < fountains.size(); i += 2) {

            var lat = fountains[i];
            var lon = fountains[i + 1];

            var d = distanciaKm(
                currentLat,
                currentLon,
                lat,
                lon
            );

            if (d < minDistance) {
                minDistance = d;
                nearestLat = lat;
                nearestLon = lon;
            }
        }

        return {
            :lat => nearestLat,
            :lon => nearestLon,
            :distance => minDistance
        };
    }

    function distanciaKm( lat1, lon1, lat2, lon2 ){

        var R = 6371.0; // Radio Tierra en km

        // Convertir grados a radianes
        var dLat = (lat2 - lat1) * Math.PI / 180.0;
        var dLon = (lon2 - lon1) * Math.PI / 180.0;

        var a =
            Math.sin(dLat / 2.0) * Math.sin(dLat / 2.0) +
            Math.cos(lat1 * Math.PI / 180.0) *
            Math.cos(lat2 * Math.PI / 180.0) *
            Math.sin(dLon / 2.0) *
            Math.sin(dLon / 2.0);

        var c = 2.0 * Math.atan2(
            Math.sqrt(a),
            Math.sqrt(1.0 - a)
        );

        return R * c;
    }
    
    function getBearing(lat1, lon1, lat2, lon2) {

        var dLon =
            (lon2 - lon1) *
            Math.PI / 180.0;

        lat1 = lat1 * Math.PI / 180.0;
        lat2 = lat2 * Math.PI / 180.0;

        var y = Math.sin(dLon) * Math.cos(lat2);

        var x =
            Math.cos(lat1) * Math.sin(lat2) -
            Math.sin(lat1) * Math.cos(lat2) *
            Math.cos(dLon);

        var brng =
            Math.atan2(y, x) *
            180.0 / Math.PI;

        while (brng < 0.0) {
            brng += 360.0;
        }

        while (brng >= 360.0) {
            brng -= 360.0;
        }

        return brng;
    }

    function bearingToText(bearing) {

        if (bearing >= 337.5 || bearing < 22.5) {
            return "N";
        }

        if (bearing < 67.5) {
            return "NE";
        }

        if (bearing < 112.5) {
            return "E";
        }

        if (bearing < 157.5) {
            return "SE";
        }

        if (bearing < 202.5) {
            return "S";
        }

        if (bearing < 247.5) {
            return "SW";
        }

        if (bearing < 292.5) {
            return "W";
        }

        return "NW";
    }

    function drawBearingArrow(dc, bearing, screenX, screenY) {
    
        var cx = screenX/2;
        var cy = screenY/2;

        var length = 60;
        var width = 20;

        var rad =
            bearing *
            Math.PI / 180.0;

        // Punta
        var tipX =
            cx + Math.sin(rad) * length;

        var tipY =
            cy - Math.cos(rad) * length;

        // Parte trasera centro
        var backX =
            cx - Math.sin(rad) * 10;

        var backY =
            cy + Math.cos(rad) * 10;

        // Lado izquierdo
        var leftX =
            backX + Math.sin(rad + Math.PI / 2.0) * width;

        var leftY =
            backY - Math.cos(rad + Math.PI / 2.0) * width;

        // Lado derecho
        var rightX =
            backX + Math.sin(rad - Math.PI / 2.0) * width;

        var rightY =
            backY - Math.cos(rad - Math.PI / 2.0) * width;

        dc.setColor(
            Graphics.COLOR_BLUE,
            Graphics.COLOR_BLUE
        );

        var points = [

            [tipX, tipY],
            [leftX, leftY],
            [rightX, rightY]
        ];

        dc.fillPolygon(points);
    }

}
