# data_basket

`data_basket` is a utility lib for conveniently save/load variables in batch, inspired by IDL's `SAVE`/`RESTORE`.

## Examples

### Basket

```python
import numpy as np
from data_basket import Basket, TextBasket

# create an empty basket.
b1 = Basket()
b1["a"] = np.random.rand(5, 3)
b1["b"] = [1, 2.5, "haha"]
b1.save('SOME/PATH.bsk')

# load 
b2 = Basket.load('SOME/PATH.bsk')

# collect from global scope
var1 = 1.5
var2 = {"a": 1, "b": np.array([1, 2, 3])}
b3 = Basket.collect(['var1', 'var2'])

# flood basket's contents into global scope
b1.flood()

# create from dict/other basket.
b4 = Basket({"a": var1, "b": var2})
b5 = Basket(b4)
b6 = TextBasket(b4)  # diffrent basket type

b6.save('SOME/PATH.tbsk')  # save a text-file-based version.

# collect from other source
class C(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
o = C()
b7 = Basket.collect(['a', 'b'], source=o, attr=True)  # when using object as source, attr=True is often required, because values are attributes of the object.

# flood into destination other than global scope
d = {}
b7.flood(dest=d)

```

### shortcuts

```python
from data_basket.shortcuts import load_basket, save_basket

load_basket('PATH/TO/SOME/BASKET/FILE')  
# Default behavior: flood the contents into global scope.

 
save_basket('PATH/TO/SOME/BASKET/FILE', ['var1', 'var2', ...])
# Default behaviour: collect specified variables from global scope and save into a basket file.
```