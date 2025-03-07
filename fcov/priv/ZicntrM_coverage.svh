///////////////////////////////////////////
//
// RISC-V Architectural Functional Coverage Covergroups
//
// Written: Corey Hickson chickson@hmc.edu 20 November 2024
// 
// Copyright (C) 2024 Harvey Mudd College, 10x Engineers, UET Lahore, Habib University
//
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
//
// Licensed under the Solderpad Hardware License v 2.1 (the “License”); you may not use this file 
// except in compliance with the License, or, at your option, the Apache License version 2.0. You 
// may obtain a copy of the License at
//
// https://solderpad.org/licenses/SHL-2.1/
//
// Unless required by applicable law or agreed to in writing, any work distributed under the 
// License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
// either express or implied. See the License for the specific language governing permissions 
// and limitations under the License.
////////////////////////////////////////////////////////////////////////////////////////////////

`define COVER_ZICNTRM
covergroup ZicntrM_mcounters_cg with function sample(ins_t ins);
    option.per_instance = 0;
    `include "coverage/RISCV_coverage_standard_coverpoints.svh"
    // Counter access in machine mode

    // building blocks for the main coverpoints
    csrrw: coverpoint ins.current.insn {
        wildcard bins csrrw = {32'b????????????_?????_001_?????_1110011}; 
    }
    csrr: coverpoint ins.current.insn {
        wildcard bins csrrw = {32'b????????????_00000_010_?????_1110011}; 
    }
    csrop: coverpoint ins.current.insn[14:12] iff (ins.current.insn[6:0] == 7'b1110011) {
        bins csrrs = {3'b010};
        bins csrrc = {3'b011};
    }
    storeop: coverpoint ins.current.insn {
        `ifdef XLEN64
            wildcard bins sd = {32'b???????_?????_?????_011_?????_0100011};
        `else
            wildcard bins sw = {32'b???????_?????_?????_010_?????_0100011};
        `endif
    }
    clint_mtime: coverpoint {ins.current.imm + ins.current.rs1_val} {
        bins mtime = {`CLINT_BASE + 32'h0000BFF8};
    }
    counters: coverpoint ins.current.insn[31:20] {
        bins mcycle        = {12'hB00};
        bins minstret      = {12'hB02};
        bins mhpmcounter3  = {12'hB03};
        bins mhpmcounter4  = {12'hB04};
        bins mhpmcounter5  = {12'hB05};
        bins mhpmcounter6  = {12'hB06};
        bins mhpmcounter7  = {12'hB07};
        bins mhpmcounter8  = {12'hB08};
        bins mhpmcounter9  = {12'hB09};
        bins mhpmcounter10 = {12'hB0A};
        bins mhpmcounter11 = {12'hB0B};
        bins mhpmcounter12 = {12'hB0C};
        bins mhpmcounter13 = {12'hB0D};
        bins mhpmcounter14 = {12'hB0E};
        bins mhpmcounter15 = {12'hB0F};
        bins mhpmcounter16 = {12'hB10};
        bins mhpmcounter17 = {12'hB11};
        bins mhpmcounter18 = {12'hB12};
        bins mhpmcounter19 = {12'hB13};
        bins mhpmcounter20 = {12'hB14};
        bins mhpmcounter21 = {12'hB15};
        bins mhpmcounter22 = {12'hB16};
        bins mhpmcounter23 = {12'hB17};
        bins mhpmcounter24 = {12'hB18};
        bins mhpmcounter25 = {12'hB19};
        bins mhpmcounter26 = {12'hB1A};
        bins mhpmcounter27 = {12'hB1B};
        bins mhpmcounter28 = {12'hB1C};
        bins mhpmcounter29 = {12'hB1D};
        bins mhpmcounter30 = {12'hB1E};
        bins mhpmcounter31 = {12'hB1F};
        bins mhpmevent3    = {12'h323};
        bins mhpmevent4    = {12'h324};
        bins mhpmevent5    = {12'h325};
        bins mhpmevent6    = {12'h326};
        bins mhpmevent7    = {12'h327};
        bins mhpmevent8    = {12'h328};
        bins mhpmevent9    = {12'h329};
        bins mhpmevent10   = {12'h32A};
        bins mhpmevent11   = {12'h32B};
        bins mhpmevent12   = {12'h32C};
        bins mhpmevent13   = {12'h32D};
        bins mhpmevent14   = {12'h32E};
        bins mhpmevent15   = {12'h32F};
        bins mhpmevent16   = {12'h330};
        bins mhpmevent17   = {12'h331};
        bins mhpmevent18   = {12'h332};
        bins mhpmevent19   = {12'h333};
        bins mhpmevent20   = {12'h334};
        bins mhpmevent21   = {12'h335};
        bins mhpmevent22   = {12'h336};
        bins mhpmevent23   = {12'h337};
        bins mhpmevent24   = {12'h338};
        bins mhpmevent25   = {12'h339};
        bins mhpmevent26   = {12'h33A};
        bins mhpmevent27   = {12'h33B};
        bins mhpmevent28   = {12'h33C};
        bins mhpmevent29   = {12'h33D};
        bins mhpmevent30   = {12'h33E};
        bins mhpmevent31   = {12'h33F};
        bins mcountinhibit = {12'h320};
    }
    `ifdef XLEN32 
        countersh: coverpoint ins.current.insn[31:20] {
            bins mcycleh        = {12'hB80};
            bins minstreth      = {12'hb82};
            bins mhpmcounter3h  = {12'hB83};
            bins mhpmcounter4h  = {12'hB84};
            bins mhpmcounter5h  = {12'hB85};
            bins mhpmcounter6h  = {12'hB86};
            bins mhpmcounter7h  = {12'hB87};
            bins mhpmcounter8h  = {12'hB88};
            bins mhpmcounter9h  = {12'hB89};
            bins mhpmcounter10h = {12'hB8A};
            bins mhpmcounter11h = {12'hB8B};
            bins mhpmcounter12h = {12'hB8C};
            bins mhpmcounter13h = {12'hB8D};
            bins mhpmcounter14h = {12'hB8E};
            bins mhpmcounter15h = {12'hB8F};
            bins mhpmcounter16h = {12'hB90};
            bins mhpmcounter17h = {12'hB91};
            bins mhpmcounter18h = {12'hB92};
            bins mhpmcounter19h = {12'hB93};
            bins mhpmcounter20h = {12'hB94};
            bins mhpmcounter21h = {12'hB95};
            bins mhpmcounter22h = {12'hB96};
            bins mhpmcounter23h = {12'hB97};
            bins mhpmcounter24h = {12'hB98};
            bins mhpmcounter25h = {12'hB99};
            bins mhpmcounter26h = {12'hB9A};
            bins mhpmcounter27h = {12'hB9B};
            bins mhpmcounter28h = {12'hB9C};
            bins mhpmcounter29h = {12'hB9D};
            bins mhpmcounter30h = {12'hB9E};
            bins mhpmcounter31h = {12'hB9F};
            bins mhpmevent3h    = {12'h723};
            bins mhpmevent4h    = {12'h724};
            bins mhpmevent5h    = {12'h725};
            bins mhpmevent6h    = {12'h726};
            bins mhpmevent7h    = {12'h727};
            bins mhpmevent8h    = {12'h728};
            bins mhpmevent9h    = {12'h729};
            bins mhpmevent10h   = {12'h72A};
            bins mhpmevent11h   = {12'h72B};
            bins mhpmevent12h   = {12'h72C};
            bins mhpmevent13h   = {12'h72D};
            bins mhpmevent14h   = {12'h72E};
            bins mhpmevent15h   = {12'h72F};
            bins mhpmevent16h   = {12'h730};
            bins mhpmevent17h   = {12'h731};
            bins mhpmevent18h   = {12'h732};
            bins mhpmevent19h   = {12'h733};
            bins mhpmevent20h   = {12'h734};
            bins mhpmevent21h   = {12'h735};
            bins mhpmevent22h   = {12'h736};
            bins mhpmevent23h   = {12'h737};
            bins mhpmevent24h   = {12'h738};
            bins mhpmevent25h   = {12'h739};
            bins mhpmevent26h   = {12'h73A};
            bins mhpmevent27h   = {12'h73B};
            bins mhpmevent28h   = {12'h73C};
            bins mhpmevent29h   = {12'h73D};
            bins mhpmevent30h   = {12'h73E};
            bins mhpmevent31h   = {12'h73F};
        }
    `endif

    walking_ones_rs1: coverpoint $clog2(ins.current.rs1_val) iff ($onehot(ins.current.rs1_val)) { 
        bins b_1[] = { [0:`XLEN-1] };
    }

    `ifdef XLEN64
        walking_ones_zeros_rs2: coverpoint ins.current.rs2_val[63:0] {
            bins b_1_0  = {64'b0000000000000000000000000000000000000000000000000000000000000001};
            bins b_1_1  = {64'b0000000000000000000000000000000000000000000000000000000000000010};
            bins b_1_2  = {64'b0000000000000000000000000000000000000000000000000000000000000100};
            bins b_1_3  = {64'b0000000000000000000000000000000000000000000000000000000000001000};
            bins b_1_4  = {64'b0000000000000000000000000000000000000000000000000000000000010000};
            bins b_1_5  = {64'b0000000000000000000000000000000000000000000000000000000000100000};
            bins b_1_6  = {64'b0000000000000000000000000000000000000000000000000000000001000000};
            bins b_1_7  = {64'b0000000000000000000000000000000000000000000000000000000010000000};
            bins b_1_8  = {64'b0000000000000000000000000000000000000000000000000000000100000000};
            bins b_1_9  = {64'b0000000000000000000000000000000000000000000000000000001000000000};
            bins b_1_10 = {64'b0000000000000000000000000000000000000000000000000000010000000000};
            bins b_1_11 = {64'b0000000000000000000000000000000000000000000000000000100000000000};
            bins b_1_12 = {64'b0000000000000000000000000000000000000000000000000001000000000000};
            bins b_1_13 = {64'b0000000000000000000000000000000000000000000000000010000000000000};
            bins b_1_14 = {64'b0000000000000000000000000000000000000000000000000100000000000000};
            bins b_1_15 = {64'b0000000000000000000000000000000000000000000000001000000000000000};
            bins b_1_16 = {64'b0000000000000000000000000000000000000000000000010000000000000000};
            bins b_1_17 = {64'b0000000000000000000000000000000000000000000000100000000000000000};
            bins b_1_18 = {64'b0000000000000000000000000000000000000000000001000000000000000000};
            bins b_1_19 = {64'b0000000000000000000000000000000000000000000010000000000000000000};
            bins b_1_20 = {64'b0000000000000000000000000000000000000000000100000000000000000000};
            bins b_1_21 = {64'b0000000000000000000000000000000000000000001000000000000000000000};
            bins b_1_22 = {64'b0000000000000000000000000000000000000000010000000000000000000000};
            bins b_1_23 = {64'b0000000000000000000000000000000000000000100000000000000000000000};
            bins b_1_24 = {64'b0000000000000000000000000000000000000001000000000000000000000000};
            bins b_1_25 = {64'b0000000000000000000000000000000000000010000000000000000000000000};
            bins b_1_26 = {64'b0000000000000000000000000000000000000100000000000000000000000000};
            bins b_1_27 = {64'b0000000000000000000000000000000000001000000000000000000000000000};
            bins b_1_28 = {64'b0000000000000000000000000000000000010000000000000000000000000000};
            bins b_1_29 = {64'b0000000000000000000000000000000000100000000000000000000000000000};
            bins b_1_30 = {64'b0000000000000000000000000000000001000000000000000000000000000000};
            bins b_1_31 = {64'b0000000000000000000000000000000010000000000000000000000000000000};
            bins b_1_32 = {64'b0000000000000000000000000000000100000000000000000000000000000000};
            bins b_1_33 = {64'b0000000000000000000000000000001000000000000000000000000000000000};
            bins b_1_34 = {64'b0000000000000000000000000000010000000000000000000000000000000000};
            bins b_1_35 = {64'b0000000000000000000000000000100000000000000000000000000000000000};
            bins b_1_36 = {64'b0000000000000000000000000001000000000000000000000000000000000000};
            bins b_1_37 = {64'b0000000000000000000000000010000000000000000000000000000000000000};
            bins b_1_38 = {64'b0000000000000000000000000100000000000000000000000000000000000000};
            bins b_1_39 = {64'b0000000000000000000000001000000000000000000000000000000000000000};
            bins b_1_40 = {64'b0000000000000000000000010000000000000000000000000000000000000000};
            bins b_1_41 = {64'b0000000000000000000000100000000000000000000000000000000000000000};
            bins b_1_42 = {64'b0000000000000000000001000000000000000000000000000000000000000000};
            bins b_1_43 = {64'b0000000000000000000010000000000000000000000000000000000000000000};
            bins b_1_44 = {64'b0000000000000000000100000000000000000000000000000000000000000000};
            bins b_1_45 = {64'b0000000000000000001000000000000000000000000000000000000000000000};
            bins b_1_46 = {64'b0000000000000000010000000000000000000000000000000000000000000000};
            bins b_1_47 = {64'b0000000000000000100000000000000000000000000000000000000000000000};
            bins b_1_48 = {64'b0000000000000001000000000000000000000000000000000000000000000000};
            bins b_1_49 = {64'b0000000000000010000000000000000000000000000000000000000000000000};
            bins b_1_50 = {64'b0000000000000100000000000000000000000000000000000000000000000000};
            bins b_1_51 = {64'b0000000000001000000000000000000000000000000000000000000000000000};
            bins b_1_52 = {64'b0000000000010000000000000000000000000000000000000000000000000000};
            bins b_1_53 = {64'b0000000000100000000000000000000000000000000000000000000000000000};
            bins b_1_54 = {64'b0000000001000000000000000000000000000000000000000000000000000000};
            bins b_1_55 = {64'b0000000010000000000000000000000000000000000000000000000000000000};
            bins b_1_56 = {64'b0000000100000000000000000000000000000000000000000000000000000000};
            bins b_1_57 = {64'b0000001000000000000000000000000000000000000000000000000000000000};
            bins b_1_58 = {64'b0000010000000000000000000000000000000000000000000000000000000000};
            bins b_1_59 = {64'b0000100000000000000000000000000000000000000000000000000000000000};
            bins b_1_60 = {64'b0001000000000000000000000000000000000000000000000000000000000000};
            bins b_1_61 = {64'b0010000000000000000000000000000000000000000000000000000000000000};
            bins b_1_62 = {64'b0100000000000000000000000000000000000000000000000000000000000000};
            bins b_1_63 = {64'b1000000000000000000000000000000000000000000000000000000000000000};
            bins b_0_0  = {64'b1111111111111111111111111111111111111111111111111111111111111110};
            bins b_0_1  = {64'b1111111111111111111111111111111111111111111111111111111111111101};
            bins b_0_2  = {64'b1111111111111111111111111111111111111111111111111111111111111011};
            bins b_0_3  = {64'b1111111111111111111111111111111111111111111111111111111111110111};
            bins b_0_4  = {64'b1111111111111111111111111111111111111111111111111111111111101111};
            bins b_0_5  = {64'b1111111111111111111111111111111111111111111111111111111111011111};
            bins b_0_6  = {64'b1111111111111111111111111111111111111111111111111111111110111111};
            bins b_0_7  = {64'b1111111111111111111111111111111111111111111111111111111101111111};
            bins b_0_8  = {64'b1111111111111111111111111111111111111111111111111111111011111111};
            bins b_0_9  = {64'b1111111111111111111111111111111111111111111111111111110111111111};
            bins b_0_10 = {64'b1111111111111111111111111111111111111111111111111111101111111111};
            bins b_0_11 = {64'b1111111111111111111111111111111111111111111111111111011111111111};
            bins b_0_12 = {64'b1111111111111111111111111111111111111111111111111110111111111111};
            bins b_0_13 = {64'b1111111111111111111111111111111111111111111111111101111111111111};
            bins b_0_14 = {64'b1111111111111111111111111111111111111111111111111011111111111111};
            bins b_0_15 = {64'b1111111111111111111111111111111111111111111111110111111111111111};
            bins b_0_16 = {64'b1111111111111111111111111111111111111111111111101111111111111111};
            bins b_0_17 = {64'b1111111111111111111111111111111111111111111111011111111111111111};
            bins b_0_18 = {64'b1111111111111111111111111111111111111111111110111111111111111111};
            bins b_0_19 = {64'b1111111111111111111111111111111111111111111101111111111111111111};
            bins b_0_20 = {64'b1111111111111111111111111111111111111111111011111111111111111111};
            bins b_0_21 = {64'b1111111111111111111111111111111111111111110111111111111111111111};
            bins b_0_22 = {64'b1111111111111111111111111111111111111111101111111111111111111111};
            bins b_0_23 = {64'b1111111111111111111111111111111111111111011111111111111111111111};
            bins b_0_24 = {64'b1111111111111111111111111111111111111110111111111111111111111111};
            bins b_0_25 = {64'b1111111111111111111111111111111111111101111111111111111111111111};
            bins b_0_26 = {64'b1111111111111111111111111111111111111011111111111111111111111111};
            bins b_0_27 = {64'b1111111111111111111111111111111111110111111111111111111111111111};
            bins b_0_28 = {64'b1111111111111111111111111111111111101111111111111111111111111111};
            bins b_0_29 = {64'b1111111111111111111111111111111111011111111111111111111111111111};
            bins b_0_30 = {64'b1111111111111111111111111111111110111111111111111111111111111111};
            bins b_0_31 = {64'b1111111111111111111111111111111101111111111111111111111111111111};
            bins b_0_32 = {64'b1111111111111111111111111111111011111111111111111111111111111111};
            bins b_0_33 = {64'b1111111111111111111111111111110111111111111111111111111111111111};
            bins b_0_34 = {64'b1111111111111111111111111111101111111111111111111111111111111111};
            bins b_0_35 = {64'b1111111111111111111111111111011111111111111111111111111111111111};
            bins b_0_36 = {64'b1111111111111111111111111110111111111111111111111111111111111111};
            bins b_0_37 = {64'b1111111111111111111111111101111111111111111111111111111111111111};
            bins b_0_38 = {64'b1111111111111111111111111011111111111111111111111111111111111111};
            bins b_0_39 = {64'b1111111111111111111111110111111111111111111111111111111111111111};
            bins b_0_40 = {64'b1111111111111111111111101111111111111111111111111111111111111111};
            bins b_0_41 = {64'b1111111111111111111111011111111111111111111111111111111111111111};
            bins b_0_42 = {64'b1111111111111111111110111111111111111111111111111111111111111111};
            bins b_0_43 = {64'b1111111111111111111101111111111111111111111111111111111111111111};
            bins b_0_44 = {64'b1111111111111111111011111111111111111111111111111111111111111111};
            bins b_0_45 = {64'b1111111111111111110111111111111111111111111111111111111111111111};
            bins b_0_46 = {64'b1111111111111111101111111111111111111111111111111111111111111111};
            bins b_0_47 = {64'b1111111111111111011111111111111111111111111111111111111111111111};
            bins b_0_48 = {64'b1111111111111110111111111111111111111111111111111111111111111111};
            bins b_0_49 = {64'b1111111111111101111111111111111111111111111111111111111111111111};
            bins b_0_50 = {64'b1111111111111011111111111111111111111111111111111111111111111111};
            bins b_0_51 = {64'b1111111111110111111111111111111111111111111111111111111111111111};
            bins b_0_52 = {64'b1111111111101111111111111111111111111111111111111111111111111111};
            bins b_0_53 = {64'b1111111111011111111111111111111111111111111111111111111111111111};
            bins b_0_54 = {64'b1111111110111111111111111111111111111111111111111111111111111111};
            bins b_0_55 = {64'b1111111101111111111111111111111111111111111111111111111111111111};
            bins b_0_56 = {64'b1111111011111111111111111111111111111111111111111111111111111111};
            bins b_0_57 = {64'b1111110111111111111111111111111111111111111111111111111111111111};
            bins b_0_58 = {64'b1111101111111111111111111111111111111111111111111111111111111111};
            bins b_0_59 = {64'b1111011111111111111111111111111111111111111111111111111111111111};
            bins b_0_60 = {64'b1110111111111111111111111111111111111111111111111111111111111111};
            bins b_0_61 = {64'b1101111111111111111111111111111111111111111111111111111111111111};
            bins b_0_62 = {64'b1011111111111111111111111111111111111111111111111111111111111111};
            bins b_0_63 = {64'b0111111111111111111111111111111111111111111111111111111111111111};
        }
    `else
        walking_ones_zeros_rs2: coverpoint ins.current.rs2_val[31:0] {
            bins b_1_0  = {32'b00000000000000000000000000000001};
            bins b_1_1  = {32'b00000000000000000000000000000010};
            bins b_1_2  = {32'b00000000000000000000000000000100};
            bins b_1_3  = {32'b00000000000000000000000000001000};
            bins b_1_4  = {32'b00000000000000000000000000010000};
            bins b_1_5  = {32'b00000000000000000000000000100000};
            bins b_1_6  = {32'b00000000000000000000000001000000};
            bins b_1_7  = {32'b00000000000000000000000010000000};
            bins b_1_8  = {32'b00000000000000000000000100000000};
            bins b_1_9  = {32'b00000000000000000000001000000000};
            bins b_1_10 = {32'b00000000000000000000010000000000};
            bins b_1_11 = {32'b00000000000000000000100000000000};
            bins b_1_12 = {32'b00000000000000000001000000000000};
            bins b_1_13 = {32'b00000000000000000010000000000000};
            bins b_1_14 = {32'b00000000000000000100000000000000};
            bins b_1_15 = {32'b00000000000000001000000000000000};
            bins b_1_16 = {32'b00000000000000010000000000000000};
            bins b_1_17 = {32'b00000000000000100000000000000000};
            bins b_1_18 = {32'b00000000000001000000000000000000};
            bins b_1_19 = {32'b00000000000010000000000000000000};
            bins b_1_20 = {32'b00000000000100000000000000000000};
            bins b_1_21 = {32'b00000000001000000000000000000000};
            bins b_1_22 = {32'b00000000010000000000000000000000};
            bins b_1_23 = {32'b00000000100000000000000000000000};
            bins b_1_24 = {32'b00000001000000000000000000000000};
            bins b_1_25 = {32'b00000010000000000000000000000000};
            bins b_1_26 = {32'b00000100000000000000000000000000};
            bins b_1_27 = {32'b00001000000000000000000000000000};
            bins b_1_28 = {32'b00010000000000000000000000000000};
            bins b_1_29 = {32'b00100000000000000000000000000000};
            bins b_1_30 = {32'b01000000000000000000000000000000};
            bins b_1_31 = {32'b10000000000000000000000000000000};
            bins b_0_0  = {32'b11111111111111111111111111111110};
            bins b_0_1  = {32'b11111111111111111111111111111101};
            bins b_0_2  = {32'b11111111111111111111111111111011};
            bins b_0_3  = {32'b11111111111111111111111111110111};
            bins b_0_4  = {32'b11111111111111111111111111101111};
            bins b_0_5  = {32'b11111111111111111111111111011111};
            bins b_0_6  = {32'b11111111111111111111111110111111};
            bins b_0_7  = {32'b11111111111111111111111101111111};
            bins b_0_8  = {32'b11111111111111111111111011111111};
            bins b_0_9  = {32'b11111111111111111111110111111111};
            bins b_0_10 = {32'b11111111111111111111101111111111};
            bins b_0_11 = {32'b11111111111111111111011111111111};
            bins b_0_12 = {32'b11111111111111111110111111111111};
            bins b_0_13 = {32'b11111111111111111101111111111111};
            bins b_0_14 = {32'b11111111111111111011111111111111};
            bins b_0_15 = {32'b11111111111111110111111111111111};
            bins b_0_16 = {32'b11111111111111101111111111111111};
            bins b_0_17 = {32'b11111111111111011111111111111111};
            bins b_0_18 = {32'b11111111111110111111111111111111};
            bins b_0_19 = {32'b11111111111101111111111111111111};
            bins b_0_20 = {32'b11111111111011111111111111111111};
            bins b_0_21 = {32'b11111111110111111111111111111111};
            bins b_0_22 = {32'b11111111101111111111111111111111};
            bins b_0_23 = {32'b11111111011111111111111111111111};
            bins b_0_24 = {32'b11111110111111111111111111111111};
            bins b_0_25 = {32'b11111101111111111111111111111111};
            bins b_0_26 = {32'b11111011111111111111111111111111};
            bins b_0_27 = {32'b11110111111111111111111111111111};
            bins b_0_28 = {32'b11101111111111111111111111111111};
            bins b_0_29 = {32'b11011111111111111111111111111111};
            bins b_0_30 = {32'b10111111111111111111111111111111};
            bins b_0_31 = {32'b01111111111111111111111111111111};
        }
    `endif

    // main coverpoints
    cp_cntr_write:      cross csrop,    walking_ones_rs1, counters,    priv_mode_m;
    cp_mtime_write:     cross storeop,  walking_ones_zeros_rs2, clint_mtime, priv_mode_m;
    `ifdef XLEN32
        cp_cntrh_write: cross csrop,    walking_ones_rs1, countersh,   priv_mode_m;
    `endif

endgroup

function void zicntrm_sample(int hart, int issue, ins_t ins);
    ZicntrM_mcounters_cg.sample(ins);
endfunction
