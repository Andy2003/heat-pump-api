HeatPump API
===

This project aims to provide a uniform abstraction layer for heat pumps.

API-Definition
---

In the file [heatpump_api.yaml](api/heatpump_api.yaml) is an AsyncAPI description, which can be edited by 
[AsyncAPI Editor](http://editor.asyncapi.org/).
It defines the endpoints to communicate with the heat pump.

Implementation
---

The script [ElsterBinding.py](bindings/elster/ElsterBinding.py) is the 1st draft to implement the API for accessing my heat pump 
`WPL-10 AC` manufactured by Stiebel Eltron. The measured values are published by the [MqttBridge.py](bridges/MqttBridge.py).

The protocol was taken from [juerg5524.ch](http://juerg5524.ch/list_data.php). The [ElsterTable](doc/ElsterTable.inc) 
is the base for the mapping used for the ElsterBinding.

Devices:

| CAN-ID | Device |
| --- | ---- |
| 180 | Boiler |
| 480 | Manager |
| 500 | Heating-unit |
| 580 | Bus-coupler |
| 680 | PC (ComfortSoft) |
| 700 | Fremdgerät |
| 780 | DCF-Modul |
    
Start Binding
---

To configure the app rename [config-template.py](config-template.py) to `config.py` and adjust the configuration to your needs.
Start the app by invoking:

    ./heat-pump.py
  
Disclaimer
===

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
