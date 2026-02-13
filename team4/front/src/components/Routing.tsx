import { Marker, Polyline, Popup, useMap } from "react-leaflet";
import polyline from "@mapbox/polyline";
import { destinationIcon, sourceIcon } from "./MapView";

const route = {
  "routes": [
    {
      "overview_polyline": {
        "points": "kz{xEggtxHn@E|@iAtMcAq@k`Ap@yO_OyA"
      },
      "legs": [
        {
          "summary": "روانمهر - ولیعصر",
          "distance": {
            "value": 1820.0,
            "text": "۲ کیلومتر"
          },
          "duration": {
            "value": 487.0,
            "text": "۸ دقیقه"
          },
          "steps": [
            {
              "name": "میدان انقلاب اسلامی",
              "instruction": "در جهت جنوب در میدان انقلاب اسلامی قرار بگیرید",
              "bearing_after": 193,
              "type": "depart",
              "modifier": "left",
              "distance": {
                "value": 61.0,
                "text": "۷۵ متر"
              },
              "duration": {
                "value": 13.0,
                "text": "کمتر از ۱ دقیقه"
              },
              "polyline": "kz{xEggtxHHBRAPGPMJSDS",
              "start_location": [51.390755, 35.701021]
            },
            {
              "name": "",
              "instruction": "به مسیر خود ادامه دهید",
              "bearing_after": 147,
              "type": "exit rotary",
              "modifier": "slight right",
              "exit": 1,
              "distance": {
                "value": 279.0,
                "text": "۳۰۰ متر"
              },
              "duration": {
                "value": 72.0,
                "text": "۱ دقیقه"
              },
              "polyline": "ww{xEcitxHXSf@Ih@EvCS~AMjCQ",
              "start_location": [51.391063, 35.700596]
            },
            {
              "name": "روانمهر",
              "instruction": "به سمت روانمهر، به چپ بپیچید",
              "bearing_after": 80,
              "type": "turn",
              "modifier": "left",
              "distance": {
                "value": 983.0,
                "text": "۱۰۰۰ متر"
              },
              "duration": {
                "value": 261.0,
                "text": "۴ دقیقه"
              },
              "polyline": "gh{xE{ktxHASC]....",
              "start_location": [51.391498, 35.698122]
            },
            {
              "name": "خسرو شکیبایی",
              "instruction": "در خسرو شکیبایی به مسیر خود ادامه دهید",
              "bearing_after": 95,
              "type": "new name",
              "modifier": "straight",
              "distance": {
                "value": 210.0,
                "text": "۲۲۵ متر"
              },
              "duration": {
                "value": 78.0,
                "text": "۱ دقیقه"
              },
              "polyline": "yi{xEuovxHXuFVuE",
              "start_location": [51.402349, 35.698366]
            },
            {
              "name": "ولیعصر",
              "instruction": "به چپ بپیچید و وارد ولیعصر شوید",
              "bearing_after": 7,
              "type": "end of road",
              "modifier": "left",
              "distance": {
                "value": 288.0,
                "text": "۳۰۰ متر"
              },
              "duration": {
                "value": 130.0,
                "text": "۲ دقیقه"
              },
              "polyline": "gh{xEa~vxHgAK{BUcCU_AKwBU",
              "start_location": [51.404651, 35.698117]
            },
            {
              "name": "ولیعصر",
              "instruction": "در مقصد قرار دارید",
              "bearing_after": 0,
              "type": "arrive",
              "distance": {
                "value": 0.0,
                "text": ""
              },
              "duration": {
                "value": 0.0,
                "text": ""
              },
              "polyline": "gx{xE{`wxH",
              "start_location": [51.405102, 35.700682]
            }
          ]
        }
      ]
    }
  ]
};

interface Props {
    overview: string;
    source: string;
    destination: string;
}

export default function Routing() {
    const overview = polyline.decode(route.routes[0].overview_polyline.points);

    const steps = route.routes[0].legs[0].steps;

const firstStep = steps[0];
const lastStep = steps[steps.length - 1];

const source: [number, number] = [
  firstStep.start_location[1], // lat
  firstStep.start_location[0], // lng
];

const destination: [number, number] = [
  lastStep.start_location[1],
  lastStep.start_location[0],
];


  return <>
    <Polyline positions={overview}/>
    <Marker position={source} icon={sourceIcon}>
          <Popup>
            <div className="text-sm font-semibold">Source</div>
          </Popup>
        </Marker>
        <Marker position={destination} icon={destinationIcon}>
          <Popup>
            <div className="text-sm font-semibold">Destination</div>
          </Popup>
        </Marker>
  </>
}
