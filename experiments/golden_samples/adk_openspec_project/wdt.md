
# 1.      范围

本文件描述CPU v3项目MSCP侧watchdog模块一些设计说明信息，方便在项目组范围内理解、使用该模块，着重描述watchdog模块的功能、接口、寄存器和使用事项等一些关键信息。

# 3.      模块功能

## 3.1.      技术要求

### 3.1.1.       模块功能说明

Ø 可配时间间隔的32位递减计时器；

Ø 超时产生中断输出信号；

Ø 若前一个超时中断没有被清除，当前计数周期内超时产生复位信号；

Ø LOCK寄存器保护看门狗模块寄存器不被失控软件更改；

Ø ID寄存器唯一标识看门狗模块。

### 3.1.3.       输入接口要求

输入接口信号wclk、wclk_en、wrst_n。输入wclk为工作时钟输入，wrst_n为工作时钟域的复位。wclk_en为工作时钟域的时钟门控，计时器在wclk_en置1的wclk上升沿工作。

### 3.1.4.       输出接口要求

输出wdogint和wdogres是wclk工作时钟域，信号列表如下：

| Name    | Width | Type | Source/Destination | Description          |
| ------- | ----- | ---- | ------------------ | -------------------- |
| wdogint | 1     | O    | System             | 看门狗中断信号，产生后没有喂狗则一直保持 |
| wdogres | 1     | O    | System             | 看门狗复位信号，产生后保持至系统复位   |

# 4.      模块设计

## 4.1.      模块的逻辑设计

工作流程简述：    
1. 设置好 Load 值与 Control 参数后，32位倒计时器开始倒计时。
2. 当计数器减到零时，根据控制寄存器中的配置：
    - 如果 `INTEN` 为1，触发 `wdogint` 中断。
    - 如果 `RESEN` 为1，再次为零时触发 `wdogres` 复位。
3. 可通过中断状态寄存器查看/清除中断状态。

系统首先配置看门狗LOCK寄存器，解锁后续关键寄存器的写访问权限，并读取相应的外设及版本信息;后配置控制寄存器和重载值寄存器开启看门狗模块的递减计数，看门狗计时器工作流程如下所示：

```
flowchart LR
    A[Watchdog is programmed] --> B[Counter reaches zero]
    B --> C[Counter reaches zero again]

    B -->|If INTEN bit in WDOGCONTROL = 1 → wdogint asserted| INT[Interrupt Triggered]
    C -->|If RESEN bit in WDOGCONTROL = 1 → wdogres asserted| RES[Reset Triggered]
```

### 4.1.5.       模块的复位说明

该模块有两个复位信号：APB总线复位信号prst_n，异步复位；wclk时钟域复位信号wrst_n，异步复位。

## 4.2.      模块寄存器说明

**4.2.1.**       **看门狗模块寄存器概述**

看门狗模块中共有21个寄存器，包括重载值寄存器WDOGLOAD、当前值寄存器WDOGVALUE、控制寄存器WDOGCONTROL、中断清除寄存器WDOGINTCLR、未屏蔽中断状态寄存器WDOGRIS、中断状态寄存器WDOGMIS、LOCK寄存器WDOGLOCK、集成测试系列寄存器WDOGITCR、WDOGITOP以及外设寄存器WDOGPERIPHID0-7、PrimeCell寄存器WDOGPCELLID0-3。

**4.2.2.**       **Watchdog Load register [0x00]**

看门狗模块重载值寄存器

地    址：0x00

寄存器名：WDOGLOAD

位    宽：32位

类    型：读写

复位时值：0xFFFFFFFF

                                Table 4       WDOGLOAD register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-0|wdog_load|R/W|0xFFFFFFFF|看门狗递减计时器重载值|

**4.2.3.**       **Watchdog Value register [0x04]**

看门狗模块递减计数当前值寄存器，读该寄存器可以获取递减计时器的当前计数值。

地    址：0x04

寄存器名：WDOGVALUE

位    宽：32位

类    型：读写

复位时值：0xFFFFFFFF

                               Table 5       WDOGVALUE register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-0|count_read|R|0xFFFFFFFF|The current value of watchdog counter<br><br>32’hffffffff: current value is 32’hffffffff<br><br>32’hfffffffe: current value is 32’hfffffffe<br><br>......<br><br>32’h00000001: current value is 32’h00000001<br><br>32’h00000000: current value is 32’h00000000|

**4.2.4.**       **Watchdog Control register [0x08]**

看门狗模块控制寄存器，该寄存器控制递减计时器的递减步进值和复位、中断及计时器使能。

地    址：0x08

寄存器名：WDOGCONTROL

位    宽：32位

类    型：读写

复位时值：0x00

                            Table 6       WDOGCONTROL register bit assigments

|      |            |     |        |                                                                                                                                                                                                                                               |
| ---- | ---------- | --- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bit  | Name       | R/W | Reset  | Description                                                                                                                                                                                                                                   |
| 31-5 | Reserved   | -   | -      | Reserved                                                                                                                                                                                                                                      |
| 4-2  | step_value | R/W | 3’b000 | 3’b000-step_value = 1, 工作时钟频率为1GHz；<br><br>3’b001-step_value = 2, 工作时钟频率为500MHz；<br><br>3’b010-step_value = 4, 工作时钟频率为250MHz；<br><br>3’b011-step_value = 8, 工作时钟频率为125MHz；<br><br>3’b100-step_value = 16,工作时钟频率为62.5MHz；<br><br>Other：invalid |
| 1    | RESEN      | R/W | 1’b0   | Enable watchdog reset output, WDOGRES. Acts as a mask for the reset output. Set to 1 to enable the reset, or to 0 to disable the reset.                                                                                                       |
| 0    | INTEN      | R/W | 1’b0   | Enable the interrupt event, WDOGINT. Set to 1 enable the counter and the interrupt. Reloads the counter from the value in WDOGLOAD when the interrupt is enable after previously being disable.                                               |

**4.2.5.**       **Watchdog Interrupt Clear register [0x0C]**

看门狗模块中断清除寄存器，该寄存器被写入任何值均可清除看门狗中断信号，并从WDOGLOAD寄存器中重载计数初值。

地    址：0x0C

寄存器名：WDOGINTCLR

位    宽：32位

类    型：只写

复位时值：0x00

**4.2.6.**       **Watchdog Raw Interrupt Status register [0x10]**

看门狗模块未屏蔽中断状态寄存器，该寄存器指示看门狗模块产生的原始中断（WS0）的状态。

地    址：0x10

寄存器名：WDOGRIS

位    宽：1位

类    型：只读

复位时值：1’b0

                                   Table 7       WDOGRIS register bit assigments

|      |                        |     |       |                                       |
| ---- | ---------------------- | --- | ----- | ------------------------------------- |
| Bit  | Name                   | R/W | Reset | Description                           |
| 31-1 | reserved               | -   | -     | -                                     |
| 0    | raw watchdog interrupt | R   | 1’b0  | Raw interrupt status from the counter |

**4.2.7.**       **Watchdog Interrupt Status register [0x14]**

看门狗模块屏蔽中断状态寄存器，该寄存器bit[0]为WDOGRIS寄存器的WS0和WDOGCONTROL寄存器的INTEN的逻辑与，即WS0 & INTEN，与中断输出值相同。

地    址：0x14

寄存器名：WDOGMIS

位    宽：1位

类    型：只读

复位时值：1’b0

                                   Table 8       WDOGMIS register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-1|reserved|-|-|-|
|0|watchdog interrupt|R|1’b0|Enable interrupt status from the counter|

**4.2.8.**       **Watchdog Lock register [0xC00]**

看门狗模块LOCK寄存器，该寄存器控制其他寄存器的写访问权限，保护失控软件对看门狗模块寄存器的恶意更改。当写入0x1ACCE551时使能其他寄存器的写权限；当写入其他值时使其他寄存器丧失写访问权限。读该寄存器时根据写入值是否为0x1ACCE551返回LOCK状态：

Ø  0 -- 寄存器写权限使能，unlock；

Ø  1 -- 寄存器写权限失效，lock。

地    址：0xC00

寄存器名：WDOGLOCK

位    宽：32位

类    型：读写

复位时值：32’h00000000

                                   Table 9       WDOGMIS register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-0|wdog_lock|R/W|32’h00000000|Enable write access to all other registers by writing 0x1ACCE551. Disable write access by writing any other value.<br><br>A read return the lock status:<br><br>0x0 -- write access to all other registers is enable, unlock;<br><br>0x1 -- write access to all other registers is disable, lock.|

**4.2.9.**       **Watchdog Integration Test Control register [0xF00]**

看门狗模块集成测试模式控制寄存器，该寄存器控制集成测试模式的使能。

地    址：0xF00

寄存器名：WDOGITCR

位    宽：1位

类    型：读写

复位时值：1’b0

                                Table 10      WDOGITCR register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-1|reserved|-|-|-|
|0|Integration test mode enable|R/W|1’b0|1 --进入集成测试模式；<br><br>0 --处于正常递减计数模式。|

**4.2.10.**    **Watchdog Integration Test Output Set register [0xF04]**

看门狗模块集成测试模式输出寄存器，当进入集成测试模式时，该寄存器直接驱动使能看门狗的中断和复位输出。

地    址：0xF04

寄存器名：WDOGITOP

位    宽：2位

类    型：只写

复位时值：2’b00

                                 Table 11      WDOGITOP register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-1|reserved|-|-|-|
|1|Integration test mode WDOGINT value|W|1’b0|集成测试模式下看门狗中断输出值|
|0|Integration test mode WDOGRES value|W|1’b0|集成测试模式下看门狗复位输出值|

**4.2.11.**    **Watchdog Peripheral Identification register 4 [0xFD0]**

看门狗模块外围设备寄存器4

地    址：0xFD0

寄存器名：WDOGPERIPHID4

位    宽：8位

类    型：只读

复位时值：8’h04

                          Table 12      WDOGPERIPHID4 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID4|R|0x04|[7:4] --block count；<br><br>[3:0] --JEP106_c_code.|

**4.2.12.**    **Watchdog Peripheral Identification register 5 [0xFD4]**

看门狗模块外围设备寄存器5

地    址：0xFD4

寄存器名：WDOGPERIPHID5

位    宽：8位

类    型：只读

复位时值：8’h00

                          Table 13      WDOGPERIPHID5 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID5|R|0x00|peripheral ID register 5, not used|

**4.2.13.**    **Watchdog Peripheral Identification register 6 [0xFD8]**

看门狗模块外围设备寄存器6

地    址：0xFD8

寄存器名：WDOGPERIPHID6

位    宽：8位

类    型：只读

复位时值：8’h00

                          Table 14      WDOGPERIPHID6 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID6|R|0x00|peripheral ID register 6, not used|

**4.2.14.**    **Watchdog Peripheral Identification register 7 [0xFDC]**

看门狗模块外围设备寄存器7

地    址：0xFDC

寄存器名：WDOGPERIPHID7

位    宽：8位

类    型：只读

复位时值：8’h00

                          Table 15      WDOGPERIPHID7 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID7|R|0x00|peripheral ID register 7, not used|

**4.2.15.**    **Watchdog Peripheral Identification register 0 [0xFE0]**

看门狗模块外围设备寄存器0

地    址：0xFE0

寄存器名：WDOGPERIPHID0

位    宽：8位

类    型：只读

复位时值：8’h24

                          Table 16      WDOGPERIPHID0 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID0|R|0x24|part number[7:0]|

**4.2.16.**    **Watchdog Peripheral Identification register 1 [0xFE4]**

看门狗模块外围设备寄存器1

地    址：0xFE4

寄存器名：WDOGPERIPHID1

位    宽：8位

类    型：只读

复位时值：8’hB8

                          Table 17      WDOGPERIPHID1 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID1|R|0xB8|[7:4]--JEP106_id_3_0<br><br>[3:0]--part number[11:8]|

**4.2.17.**    **Watchdog Peripheral Identification register 2 [0xFE8]**

看门狗模块外围设备寄存器2

地    址：0xFE8

寄存器名：WDOGPERIPHID2

位    宽：8位

类    型：只读

复位时值：8’h1B

                          Table 18      WDOGPERIPHID2 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PERIPH_ID2|R|0x1B|[7:4]--Revision<br><br>[3]--JEDEC_used<br><br>[2:0]--JEP106_id_6_4|

**4.2.18.**    **Watchdog Peripheral Identification register 3 [0xFEC]**

看门狗模块外围设备寄存器3

地    址：0xFEC

寄存器名：WDOGPERIPHID3

位    宽：8位

类    型：只读

复位时值：8’h00

                          Table 19      WDOGPERIPHID3 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-4|ECOREVNUM|R|0x0|ECO revision number|
|3-0|WDOG_PERIPH_ID3|R|0x0|Customer modification number|

**4.2.19.**    **Watchdog Prime Cell register 0 [0xFF0]**

看门狗模块Prime Cell寄存器0

地    址：0xFF0

寄存器名：WDOGPECELLID0

位    宽：8位

类    型：只读

复位时值：8’h0D

                           Table 20      WDOGPCELLID0 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PCELL_ID0|R|0x0D|Component ID register 0|

**4.2.20.**    **Watchdog Prime Cell register 0 [0xFF4]**

看门狗模块Prime Cell寄存器1

地    址：0xFF4

寄存器名：WDOGPECELLID1

位    宽：8位

类    型：只读

复位时值：8’hF0

                           Table 21      WDOGPCELLID1 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PCELL_ID1|R|0xF0|Component ID register 1|

**4.2.21.**    **Watchdog Prime Cell register 2 [0xFF8]**

看门狗模块Prime Cell寄存器2

地    址：0xFF8

寄存器名：WDOGPECELLID2

位    宽：8位

类    型：只读

复位时值：8’h05

                           Table 22      WDOGPCELLID2 register bit assigments

|   |   |   |   |   |
|---|---|---|---|---|
|Bit|Name|R/W|Reset|Description|
|31-8|reserved|-|-|-|
|7-0|WDOG_PCELL_ID2|R|0x05|Component ID register 2|

**4.2.22.**    **Watchdog Prime Cell register 3 [0xFFC]**

看门狗模块Prime Cell寄存器3

地    址：0xFFC

寄存器名：WDOGPECELLID3

位    宽：8位

类    型：只读

复位时值：8’hB1

                           Table 23      WDOGPCELLID3 register bit assigments

|      |                |     |       |                         |
| ---- | -------------- | --- | ----- | ----------------------- |
| Bit  | Name           | R/W | Reset | Description             |
| 31-8 | reserved       | -   | -     | -                       |
| 7-0  | WDOG_PCELL_ID3 | R   | 0xB1  | Component ID register 3 |
|      |                |     |       |                         |

