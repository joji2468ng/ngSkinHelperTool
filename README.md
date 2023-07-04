# ngSkinHelperTool

Helper Tool for ngSkinTools1 and ngSkinTools2.  
I've recently developed this tool under the supervision of a lead rigger in ReelFX.

https://vimeo.com/841102271?share=copy

This tool contains 4 main tabs  ["CopyPaste", "Build", "Mirror", "Utils"] to help your skin process when using ngSkinTools.   
Also seamlessly implement the functions between ngSkinTools1 and ngSkinTools2. For each description of Tabs, please see the following.

Here are some features of the helper tool:

## CopyPaste Tab
・It allows for the copying and pasting of multiple joints between different layers  
by replacing occurrences of a specified substring within a string with another substring all at once.  

![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/82de796a-6558-4208-8b1c-4be31bc15dc0)

## Build Tab
・Users can create customized presets for frequently used layers,   
which can then be easily applied to the selected mesh.  

・It enables the assignment of initial weights to facial features(brow, eyelid, squints, etc.).  
In addition, After assigning the weights, it fills transparency in a way that respects the edge flow, thanks to the ngSkinTools2 feature.

![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/b0b40836-a917-4b18-9306-5a58c5c3262f)


## Mirror Tab
・With Mirror Layer Effects, you can easily set up the layer effects type in each layer, bypassing manual settings.

・Mirror Influences in All Layers allows you to mirror the weights of all layers  
　on the selected ng mesh, or all ng-meshes in the scene, simultaneously.
 
![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/5fa7b091-0009-4633-b955-6f48a1a9ecb7)

## Utils Tab
・It provides the ability to convert layer data to upgrade or downgrade the version of ngSkinTools.

・The Weight Clipboard feature lets you copy weights and paste them to a layer on another  
   mesh. There's a known bug in ngSkinTools2 that prevents pasting to a layer on a different mesh.
   
![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/4aa2ad8e-9af1-4b47-a4de-540d3204634c)

