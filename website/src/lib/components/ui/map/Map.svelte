<script>
  import { onMount, onDestroy } from "svelte";
  import { Map, MercatorCoordinate, Marker, GeolocateControl } from "maplibre-gl";
  import { mapCenter, mode, selected } from "$lib/store/store";
  import "maplibre-gl/dist/maplibre-gl.css";
  import "$lib/customLib/three.min.js";
  import "$lib/customLib/ObjLoader.js";
  import "$lib/customLib/suncalc.min.js";
    import { createEventDispatcher } from "svelte";

  let center;
  export let pins;
  
	
	let mapInit = {
	  lng : 109.10254585419385,
      lat : -6.87025589312134,
      zoom : 14
	}
	

	
	// console.log("center",center)
  
  // export let offsets;

  let THREE;
  let initialState;
  let initialPinsCount;
  let marker;
  let modelLayerExist = false;

  let map;
  let mapContainer;
  let rotateEnable = false;
//  const apiKey = import.meta.env.MAP_API;
  const apiKey = "UqRPjSVQtdcGNELUlawm";

  const markers = [];
  // Create an event dispatcher
  const dispatch = createEventDispatcher();
  
  function updateIndex(param) {
    // Emit the 'update' event with the updated object and index
    dispatch("clicked", param);
  }

  function rotateCamera() {
    if (rotateEnable) {
      setTimeout(() => {
        map.rotateTo(map.getBearing() + 0.5, { duration: 0 });
      }, 100);
    }
    requestAnimationFrame(rotateCamera);
  }

  function addMarkers(pins) {
    // Select all div elements with the specific class
    const markersToRemove = document.querySelectorAll(
      ".marker_type, .marker_status"
    );

    // Iterate over the NodeList and remove each marker
    markersToRemove.forEach((marker) => {
      marker.remove();
    });

    pins.forEach((location, index) => {
      const el = document.createElement("div");
      el.className = "marker_type";

      // create a div for the marker_status
      const ol = document.createElement("div");
      ol.className = "marker_status";
      ol.style.backgroundImage = `url(assets/markers/${location.status}.png`;
      // Adjust width and height as needed
      ol.style.width = "60px";
      ol.style.height = "60px";

      // append the marker_status
      el.appendChild(ol);
      // console.log(location.type, location.status);
      el.style.backgroundImage = `url(assets/markers/${location.type}.png`;

      el.addEventListener("click", () => {
        selected.set(index + 1);
      });

      let pin = new Marker({ element: el })
        .setLngLat([location.lng, location.lat])
        .addTo(map);
      markers.push(pin);
    });
  }

  function addModelLayers(index) {
    const currentDate = new Date(); // Use the current date and time '2023-09-10T08:30:00'

    const sunPosition = SunCalc.getPosition(
      currentDate,
      initialState.lat,
      initialState.lng
    );

    const { altitude, azimuth } = sunPosition;

    const sunDirection = new THREE.Vector3(
      Math.cos(altitude) * Math.cos(azimuth),
      Math.sin(altitude),
      Math.cos(altitude) * Math.sin(azimuth)
    ).normalize();

    let pin = pins[index - 1];
    // // // console.log('pin',index,pin)
    const modelOrigin = [pin.lng, pin.lat];
    const modelAltitude = 0;
    const modelRotate = [Math.PI / 2, 0, 0]; // * pin.rot

    const modelAsMercatorCoordinate = MercatorCoordinate.fromLngLat(
      modelOrigin,
      modelAltitude
    );

    // transformation parameters to position, rotate and scale the 3D model onto the map
    const modelTransform = {
      translateX: modelAsMercatorCoordinate.x,
      translateY: modelAsMercatorCoordinate.y,
      translateZ: modelAsMercatorCoordinate.z,
      rotateX: modelRotate[0],
      rotateY: modelRotate[1],
      rotateZ: modelRotate[2],

      scale: modelAsMercatorCoordinate.meterInMercatorCoordinateUnits(),
    };

    const customLayer = {
      id: "3d-model",
      type: "custom",
      renderingMode: "3d",
      onAdd(map, gl) {
        this.scene = new THREE.Scene();
        this.camera = new THREE.Camera();
        this.map = map;

        const loader = new THREE.OBJLoader();

        loader.load(`assets/3d/${pin.type}.obj`, (model) => {
          // const model = chargerModel.scene;
          model.traverse((node) => {
            if (node instanceof THREE.Mesh) {
              node.castShadow = true;
              node.receiveShadow = true;
              // // // console.log(node);
            }
          });

          this.scene.add(model);
        });

        const groundGeometry = new THREE.CircleGeometry(15, 32);

        const groundMaterial = new THREE.MeshStandardMaterial({
          color: 0xffffff, // Set the color of the glass
          transparent: true,
          opacity: 0.1, // Adjust the opacity for transparency
          // transmission: 1, // Enable full light transmission for glass
        }); // White color

        const ground = new THREE.Mesh(groundGeometry, groundMaterial);

        ground.receiveShadow = true; // Allow the ground to receive shadows
        ground.rotation.x = -Math.PI / 2; // Rotate the ground to be horizontal
        this.scene.add(ground);

        // use the MapLibre GL JS map canvas for three.js
        this.renderer = new THREE.WebGLRenderer({
          canvas: map.getCanvas(),
          context: gl,
          antialias: false,
        });

        this.renderer.autoClear = false;
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.BasicShadowMap; // default THREE.PCFShadowMap

        // create two three.js lights to illuminate the model

        const light = new THREE.DirectionalLight(0xffffff, 1);

        light.position.set(
          12 * sunDirection.x,
          12 * sunDirection.y,
          12 * sunDirection.z
        );
        // // // console.log("light.position",light.position);
        light.castShadow = true;
        light.shadow.mapSize.width = 2048;
        light.shadow.mapSize.height = 2048;
        light.shadow.camera.near = 0.1;
        light.shadow.camera.far = 30;
        light.shadow.camera.left = -50;
        light.shadow.camera.right = 50;
        light.shadow.camera.top = 50;
        light.shadow.camera.bottom = -50;
        this.scene.add(light);

        const cubeGeometry = new THREE.BoxGeometry();
        const cubeMaterial = new THREE.MeshStandardMaterial({
          color: 0x00ff00,
        });
        const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
        cube.castShadow = true;
        cube.position.set(light.position);
        this.scene.add(cube);
      },

      render(gl, matrix) {
        const rotationX = new THREE.Matrix4().makeRotationAxis(
          new THREE.Vector3(1, 0, 0),
          modelTransform.rotateX
        );
        const rotationY = new THREE.Matrix4().makeRotationAxis(
          new THREE.Vector3(0, 1, 0),
          modelTransform.rotateY
        );
        const rotationZ = new THREE.Matrix4().makeRotationAxis(
          new THREE.Vector3(0, 0, 1),
          modelTransform.rotateZ
        );

        const m = new THREE.Matrix4().fromArray(matrix);
        const l = new THREE.Matrix4()
          .makeTranslation(
            modelTransform.translateX,
            modelTransform.translateY,
            modelTransform.translateZ
          )
          .scale(
            new THREE.Vector3(
              modelTransform.scale,
              -modelTransform.scale,
              modelTransform.scale
            )
          )
          .multiply(rotationX)
          .multiply(rotationY)
          .multiply(rotationZ);

        this.camera.projectionMatrix = m.multiply(l);
        this.renderer.resetState();
        this.renderer.render(this.scene, this.camera);
        this.map.triggerRepaint();
      },
    };

    map.addLayer(customLayer);
    // // console.log("map.addLayer", customLayer);
    modelLayerExist = true;
  }

  onMount(() => {
    
    initialState = { lng: center.lng, lat: center.lat };

    map = new Map({
      container: mapContainer,
      style: `https://api.maptiler.com/maps/ea513a9b-2631-40fb-ad08-a2b12367127c/style.json?key=${apiKey}`,
      center: [initialState.lng, initialState.lat],
      pitch: 0,
      antialias: true,
      zoom: 14,
      attributionControl: false,
    });

    /* map.easeTo({
      offsets,
      duration: 1000,
    }); */

    rotateCamera(0);

    THREE = window.THREE;

    if (pins)
      map.on("style.load", () => {
        initialPinsCount = pins.length;
        addMarkers(pins);
      });

    // Listen for the map move event
    map.on("move", () => {
      const center = map.getCenter();
      // Update the store with the new map center position
      mapCenter.set({
        lng: center.lng,
        lat: center.lat,
      });

      if (marker) {
        const center = map.getCenter();
        marker.setLngLat([center.lng, center.lat]);
      }
    });

    // Add geolocate control to the map.
    map.addControl(
        new GeolocateControl({
            positionOptions: {
                enableHighAccuracy: true
            },
            trackUserLocation: true
        }), 'top-right'
    );

    initialPinsCount = pins.length;
  });

  // Listen for changes in the $mode store
  $: if (map && $mode == "Add") {
    const center = map.getCenter();
    marker = new Marker().setLngLat([center.lng, center.lat]).addTo(map);
  } else if (marker) {
    marker.remove();
  }

  // Listen for changes in the $$selected store
  $: {
      if (map && $selected) {
        setTimeout(() => {
          addModelLayers($selected);
        }, 1000);
        setTimeout(() => {
          rotateEnable = true;
        }, 2000);
      } else {
        if (modelLayerExist) {
          setTimeout(() => {
            map.removeLayer("3d-model");
          }, 300);
          modelLayerExist = false;
        }
        rotateEnable = false;
      }
      markers.forEach((marker) => {
        marker.getElement().style.opacity = $selected ? 0 : 1;
      });
	  if ($selected > 0) {
		  // console.log("map",pins,$selected)
		  center = {
			lng: pins[$selected -1].lng,
			lat: pins[$selected - 1].lat,
		  };
		} else {
			center = { lng: mapInit.lng, lat: mapInit.lat, zoom : mapInit.zoom };
		}

      setTimeout(() => {
        map.flyTo({
          center: [center.lng, center.lat],
          pitch: $selected ? 45 : 0,
          zoom: $selected ? 20 : 14,
          speed: 2, // make the flying slow
          curve: 2, // change the speed at which it zooms out
          essential: true,
        });
      }, 100);
  }

  // Listen for changes in the pins.length
  $: if (map && pins.length != initialPinsCount) {
      addMarkers(pins);
      initialPinsCount = pins.length;
    }
  // Listen for changes in the padding
  /* $: if (map) {
    let padding = offsets;
    map.easeTo({
      padding,
      duration: 1000,
    });
  } */

  onDestroy(() => {
    map.remove();
  });
</script>

  <div class="map-wrap" bind:this={mapContainer} />


<style>
  .hidden{
    display:none;
  }

  .map-wrap {
    width: inherit;
    height: inherit;
    position:relative;
    box-sizing: border-box;
    overflow: hidden;
    
    border: 2px solid var(--border);
  }

  .marker_type {
    display: block;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    padding: 0;
    transition: opacity 0.5s ease-in-out;
  }
</style>
