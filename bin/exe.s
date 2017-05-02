.text
.globl   main
main:

lw $t3, x_main
li $t3, 3
sw $t3, x_main
lw $t4, y_main
li $t4, 3
sw $t4, y_main
lw $t5, _t1_main
lw $t5, x_main
sw $t5, _t1_main
lw $t6, _t2_main
lw $t6, y_main
sw $t6, _t2_main
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $t7, _t1_main
sw $t7, 0($a0)
addi $a0, $a0, -4
lw $t8, _t2_main
sw $t8, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal ackermann
addu $sp, $fp, $0
lw $t9, _t3_main
move $t9, $v1
sw $t9, _t3_main
lw $s0, output_main
lw $s0, _t3_main
sw $s0, output_main
li $v0, 4
la $a0, cout_59
syscall
li $v0, 1
lw $a0, output_main
syscall
lw $ra, 0($sp)
lw $fp, -4($sp)
li $v0, 10
syscall



ackermann:
addi $sp, $sp, -36
sw $ra, 0($sp)
sw $fp, -4($sp)
addu $fp, $0, $sp
lw $t0, count_global
addi $t0, $t0, 1
sw $t0, count_global
li $v0, 4
la $a0, cout_3
syscall
li $v0, 1
lw $a0, 44($sp)
syscall
li $v0, 4
la $a0, cout_5
syscall
li $v0, 1
lw $a0, 40($sp)
syscall
li $v0, 4
la $a0, cout_7
syscall
li $v0, 1
lw $a0, count_global
syscall
li $v0, 4
la $a0, cout_9
syscall
lw $t1, 44($sp)
blt $t1, 0, L_14
b L_12
L_12:
lw $t2, 40($sp)
blt $t2, 0, L_14
b L_16
L_14:
lw $t3, 36($sp)
li $t3, -1
sw $t3, 36($sp)
lw $t4, 36($sp)
addu $v1, $t4, $0
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
L_16:
lw $t5, 44($sp)
beq $t5, 0, L_18
b L_21
L_18:
lw $t6, 36($sp)
lw $t7, 40($sp)
addi $t6, $t7, 1
sw $t6, 36($sp)
lw $t8, 32($sp)
lw $t8, 36($sp)
sw $t8, 32($sp)
lw $t9, 32($sp)
addu $v1, $t9, $0
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
L_21:
lw $s0, 40($sp)
beq $s0, 0, L_23
b L_32
L_23:
lw $s1, 36($sp)
lw $s2, 44($sp)
li $s3, 1
sub $s1, $s2, $s3
sw $s1, 36($sp)
lw $s4, 32($sp)
lw $s4, 36($sp)
sw $s4, 32($sp)
lw $s5, 28($sp)
li $s5, 1
sw $s5, 28($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s6, 32($sp)
sw $s6, 0($a0)
addi $a0, $a0, -4
lw $s7, 28($sp)
sw $s7, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal ackermann
addu $sp, $fp, $0
lw $t0, 24($sp)
move $t0, $v1
sw $t0, 24($sp)
lw $t1, 20($sp)
lw $t1, 24($sp)
sw $t1, 20($sp)
lw $t2, 20($sp)
addu $v1, $t2, $0
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
L_32:
lw $t3, 36($sp)
lw $t4, 44($sp)
li $t5, 1
sub $t3, $t4, $t5
sw $t3, 36($sp)
lw $t6, 32($sp)
lw $t7, 40($sp)
li $t8, 1
sub $t6, $t7, $t8
sw $t6, 32($sp)
lw $t9, 28($sp)
lw $t9, 44($sp)
sw $t9, 28($sp)
lw $s0, 24($sp)
lw $s0, 32($sp)
sw $s0, 24($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s1, 28($sp)
sw $s1, 0($a0)
addi $a0, $a0, -4
lw $s2, 24($sp)
sw $s2, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal ackermann
addu $sp, $fp, $0
lw $s3, 20($sp)
move $s3, $v1
sw $s3, 20($sp)
lw $s4, 16($sp)
lw $s4, 36($sp)
sw $s4, 16($sp)
lw $s5, 12($sp)
lw $s5, 20($sp)
sw $s5, 12($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s6, 16($sp)
sw $s6, 0($a0)
addi $a0, $a0, -4
lw $s7, 12($sp)
sw $s7, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal ackermann
addu $sp, $fp, $0
lw $t0, 8($sp)
move $t0, $v1
sw $t0, 8($sp)
lw $t1, 4($sp)
lw $t1, 8($sp)
sw $t1, 4($sp)
lw $t2, 4($sp)
addu $v1, $t2, $0
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra


.data

count_global: .word 0
cout_3: .asciiz "x: "
cout_5: .asciiz "y: "
cout_7: .asciiz "count: "
cout_9: .asciiz "\n"
cout_59: .asciiz "ackermann: "
x_main: .word 0
y_main: .word 0
_t1_main: .word 0
_t2_main: .word 0
_t3_main: .word 0
output_main: .word 0
