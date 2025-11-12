; Assembly Code Generation Output
; ===============================

.DATA
    ; Variable declarations would go here

.CODE
START:
    ; Main program entry point
    CALL FUNC_main
    HLT

; Assembly Code Generation Output
; ===============================

Intermediate Code Generation Output:
    MOV ================================================, =
    ; Intermediate Code Generation Output
    ; ===================================
    ; Function: int main

FUNC_main:
    PUSH BP
    MOV BP, SP
    ; Declare int x
    MOV x, 10
    ; Declare float y
    MOV y, 5.5
    ; Declare int result
    ; Unprocessed: t1 = x > 5
    CMP t1, 0
    JE L1
    MOV t2, x
    ADD t2, y
    MOV result, t2
    ; Expression: result
    JMP L2
L1:
    MOV t3, x
    SUB t3, y
    MOV result, t3
    ; Expression: result
L2:
L3:
    ; Unprocessed: t4 = x > 0
    CMP t4, 0
    JE L4
    MOV t5, x
    SUB t5, 1
    MOV x, t5
    ; Expression: x
    JMP L3
L4:
    MOV i, 0
L5:
    ; Unprocessed: t6 = i < 5
    CMP t6, 0
    JE L7
    JMP L6
L6:
    MOV t7, result
    ADD t7, i
    MOV result, t7
    ; Expression: result
    MOV t8, i
    ADD t8, 1
    MOV i, t8
    JMP L5
L7:
    MOV R0, result
    POP BP
    RET
    POP BP
    RET
    ; Function: float calculate

FUNC_calculate:
    PUSH BP
    MOV BP, SP
    PUSH a
    PUSH b
    MOV t9, a
    MUL t9, b
    MOV t10, t9
    ADD t10, 2.0
    MOV R0, t10
    POP BP
    RET
    POP BP
    RET
