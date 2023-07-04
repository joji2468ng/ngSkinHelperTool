# ngSkinHelperTool

Helper Tool for ngSkinTools1 and ngSkinTools2.  
I've recently developed this tool under the supervision of a lead rigger in ReelFX.

https://vimeo.com/841102271?share=copy

This tool contains 4 main tabs  *["CopyPaste", "Build", "Mirror", "Utils"]* to help your skin process when using ngSkinTools.   
Also seamlessly implement the functions between ngSkinTools1 and ngSkinTools2.   
For each description of Tabs, please see the following.

## CopyPaste Tab
・It allows for the copying and pasting of multiple joints between different layers  
by replacing occurrences of a specified substring within a string with another substring all at once.   
This can be done using one of the options among ["Replace", "Add", "Subtract" or "Cut"].

![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/63e251d4-ab83-46b7-9315-ed4b9756a362)

## Build Tab
・Users can create customized presets for frequently used layers, which can then be easily applied to the selected mesh.  
This approach can streamline the workflow, saving time and effort when working on the asset.  

・It enables the assignment of initial weights to facial features(brow, eyelid, squints, etc.).  
In addition, After assigning the weights, it fills transparency in a way that respects the edge flow, thanks to the ngSkinTools2 feature.

![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/3f34bb0c-bca7-40f2-b727-dc27877234dc)


## Mirror Tab
・With Mirror Layer Effects, you can easily set up the layer effects type in each layer, bypassing manual settings.

・Mirror Influences in All Layers allows you to mirror the weights of all layers  
　on the selected ng mesh, or all ng-meshes in the scene, simultaneously.
 
![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/74881f72-45d4-4fe9-87f0-42b3641fa548)

## Utils Tab
・It provides the ability to convert layer data to upgrade or downgrade the version of ngSkinTools.  
This conversion process depends on the version you are using. This approach allows us to transition between ngSkinTool1 and 2.  
So that if something goes wrong when you use ngSkinTools2 for some crazy reason, you can always revert to v1  
without losing the skinning layers. Or if a character has already started with one, Or even if a rigger prefers one over two they can choose.  

・The Weight Clipboard feature lets you copy weights and paste them to a layer on another  
   mesh. There's a known bug in ngSkinTools2 that prevents pasting to a layer on a different mesh.
   
![image](https://github.com/maglev2468ng/ngSkinHelperTool/assets/11863299/7ae33d54-6a79-4b40-8027-450dddf00b48)

