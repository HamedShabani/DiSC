### Simple Explanation (no background needed)

- **What is a “moment”?**  
  Think of a moment as a **twisting force**. Instead of just pushing straight in, your pins can also create a twist around the skull’s center. If that twist gets too big, the clamp will start to turn/slip.

- **What is “penetration depth”?**  
  When each pin pushes in, it sinks a tiny bit into the bone (or phantom). If one pin goes in more than another, the clamp sits unevenly and can wobble. We measure how far each pin sinks (based on the force sensor reading) and take the difference between the deepest and shallowest pin.

- **Where do the numbers come from?**  
  - **Forces** come directly from your **force sensors** on each pin.  
  - **Pin positions** (for computing the twist) come from your **tracker markers**.  
  - We combine both readings so that the Stability Index goes down if either the twist is large or the depth difference is large.

This way, even without a biomechanics degree, you can see the model:  
1. We penalize big twists (moments).  
2. We penalize uneven pin depths.  
3. We blend those penalties into one number (SI) that tells you at a glance how safe your clamp is.  
