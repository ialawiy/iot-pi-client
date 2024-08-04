<script>
import "../app.css";   import { ModeWatcher } from "mode-watcher";
import { onMount } from "svelte";
import { auth, db } from "$lib/firebase/firebase";
import { getDoc, doc, setDoc, onSnapshot, collection, getDocs } from "firebase/firestore";
import { stores, notify, userMode, mode, docTree } from "$lib/store/store";

const nonAuthRoutes = ["/", "product"];

function showNotification(changed) {
  const title = changed.name;
  const options = {
    body: 'Parameter Updated.',
    icon: 'favicon.png'
  };
  new Notification(title, options);
}

onMount(() => {
  
  const unsubscribeAuth = auth.onAuthStateChanged(async (user) => {
    const currentPath = window.location.pathname;
    console.log(currentPath)

    if (!user && !nonAuthRoutes.includes(currentPath)) {
      window.location.href = "/";
      return;
    }

    if (user && currentPath === "/") {
	  window.location.href = "/dashboard?mode=Home";
      return;
    }
    
    if (user && currentPath === "/dashboard") {

      let dataToSetToStore;
      let publicData;

      const userDocRef = doc(db, "user", user.uid);
      const userdocSnap = await getDoc(userDocRef);
	  
	async function getUserNodeIds(userId) {
	  const nodesSnapshot = await getDocs(collection(db, 'user', userId, 'nodes'));
	  const nodes = nodesSnapshot.docs.map(doc => ({
		id: doc.id,
		name: doc.data().name // Include the 'name' field from the 'nodes' documents
	  }));
	  return nodes;
	}

	async function getUserIds() {
	  const usersSnapshot = await getDocs(collection(db, 'user'));
	  const users = usersSnapshot.docs.map(doc => ({
		userId: doc.id,
		details: doc.data() // Include the 'email' field from the 'user' documents
	  }));

	  return Promise.all(users.map(async (user) => {
		const nodes = await getUserNodeIds(user.userId);
		return { ...user, nodes }; // Combine user info with their nodes
	  }));
	}
	
	getUserIds().then(users => {
	  docTree.set(users);
	  console.log("docTree",$docTree);
	});
      
      if (!userdocSnap.exists()) {
          console.log("Creating User");
          dataToSetToStore = {
            profile: {
              email: user.email
            },
          };
          await setDoc(userDocRef, dataToSetToStore, { merge: true });
        } else {
          console.log("Fetching User");
          if (user.email == 'public@user.com') $userMode = "public";
          else if (user.email == 'admin@user.com') { $userMode = "admin"; $mode = "Admin" }
		  console.log("usertype",$userMode)
		  const userData = userdocSnap.data();
          dataToSetToStore = userData;
          console.log(userData);
        }

      // Fetch the subcollection 'nodes'
      const subCollectionRef = collection(db, "user", user.uid, "nodes");
      const subCollectionSnap = await getDocs(subCollectionRef);
      let subCollectionData = [];
      
      if (subCollectionSnap.empty) {
        console.log("'nodes' subcollection is currently empty.");
      } else {
        // Subcollection exists and has documents
        subCollectionSnap.forEach((doc) => {
          let docData = doc.data();
          subCollectionData.push(docData);
        });
        console.log("Subcollection exist",subCollectionData);
      }

      // Combine user data with subcollection data
      dataToSetToStore.nodes = subCollectionData;
      // Listen for changes to the Firestore document associated with the user
      const unsubscribeFirestore = onSnapshot(userDocRef, (docSnap) => {
        
        const userData = docSnap.data();
        dataToSetToStore = userData;
        dataToSetToStore.nodes = subCollectionData;
        stores.update((curr) => ({
          ...curr,
          user,
          data: dataToSetToStore,
          loading: false,
        }));
      });

      // Listen for changes in the 'nodes' subcollection
      const unsubscribeNodes = onSnapshot(subCollectionRef, (querySnapshot) => {
        querySnapshot.docChanges().forEach((change) => {
          if (change.type === "added" || change.type === "modified") {
            // Get the changed document data
            const changedDocData = change.doc.data();
            if ($notify && change.type === "modified") {
              Notification.requestPermission().then((result) => {
                if (result === 'granted') {
                  showNotification(changedDocData);
                }
              });
            }
            // Update the store with the changed document data
            stores.update((curr) => {
              // Create a new nodes array or use the existing one
              const updatedNodes = curr.data.nodes ? [...curr.data.nodes] : [];
              // Find the index of the document that changed
              const docIndex = updatedNodes.findIndex((doc) => doc.id === change.doc.id);
              if (docIndex !== -1) {
                // Replace the old document data with the new data
                updatedNodes[docIndex] = changedDocData;
              } else {
                // Add the new document data to the nodes array
                updatedNodes.push(changedDocData);
              }
              return {
                ...curr,
                data: {
                  ...curr.data,
                  nodes: updatedNodes,
                },
              };
            });
          }
          if (change.type === "removed") {
            // Handle the removed document
            stores.update((curr) => {
              const updatedNodes = curr.data.nodes.filter((doc) => doc.id !== change.doc.id);
              return {
                ...curr,
                data: {
                  ...curr.data,
                  nodes: updatedNodes,
                },
              };
            });
          }
        });
      });

	
	  
		return () => {
        unsubscribeAuth(); // Unsubscribe from Firebase auth changes
        unsubscribeFirestore(); // Unsubscribe from Firestore document changes
        unsubscribeNodes(); // Unsubscribe from 'nodes' subcollection changes
      };

    }

    if (!user) {
      return;
    }
  });
});
</script>

<ModeWatcher />
<main class="mainContainer">
    <slot></slot>
</main>

<style>    

    .mainContainer {
      overflow: auto; /* Prevents scrollbar if iframe content fits */
      scrollbar-width: none;
    }
  
    .mainContainer::-webkit-scrollbar {
      display: none;
    }
	
  </style>