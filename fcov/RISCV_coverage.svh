//
// Copyright (c) 2023 Imperas Software Ltd., www.imperas.com
// Modified February 2024, jcarlin@hmc.edu
//
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
// either express or implied.
//
// See the License for the specific language governing permissions and
// limitations under the License.
//
//

`include "coverage/RISCV_coverage_pkg.svh"

import RISCV_coverage_pkg::*;

class coverage #(
  parameter int ILEN   = 32,  // Instruction length in bits
  parameter int XLEN   = 32,  // GPR length in bits
  parameter int FLEN   = 32,  // FPR length in bits
  parameter int VLEN   = 512, // Vector register size in bits
  parameter int NHART  = 1,   // Number of harts reported
  parameter int RETIRE = 1    // Number of instructions that can retire during valid event
) extends RISCV_coverage #(ILEN, XLEN, FLEN, VLEN, NHART, RETIRE);

  function new(virtual rvviTrace #(ILEN, XLEN, FLEN, VLEN, NHART, RETIRE) rvvi);
    super.new(rvvi);
  endfunction

  function void sample(bit trap, int hart, int issue, string disass);
    save_rvvi_data(trap, hart, issue, disass);
    sample_extensions(hart, issue);
  endfunction
endclass
