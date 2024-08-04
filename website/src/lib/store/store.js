import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { writable } from "svelte/store";
import { auth } from "$lib/firebase/firebase";

export const stores = writable({
    user: null,
    loading: true,
    data: {
        nodes: []
    }
})

export const userAuth = {
    signup: async (email, pass) => {
        await createUserWithEmailAndPassword(auth, email, pass)
    },
    login: async (email, pass) => {
        await signInWithEmailAndPassword(auth, email, pass)
    },
    logout: async () => {
        await signOut(auth)
    }
}

export const selected = writable(0);

export const mode = writable("Home");

export const notify = writable(false);

export const valueChange = writable(false);

export let userMode = writable("user");

export let docTree = writable([]);

export const mapCenter = writable({ 
	lat: null,
    lng: null,
}); // Replace with your initial center coordinates
  
export const model3d = writable([{ 
	lat: null,
    lng: null,
    type: null,
	rot: null
	}]);
	
 // Create a writable store for panelList
 export const panelListStore = writable([
    // ... (your panelList data)
  ]);