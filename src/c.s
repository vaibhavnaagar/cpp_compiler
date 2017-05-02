.text
.globl   main
main:

li $v0, 4
la $a0, cout_24
syscall
lw $t0, _t1_main
lw $t1, arr_size_global
li $t2, 1
sub $t0, $t1, $t2
sw $t0, _t1_main
lw $t3, _t2_main
li $t3, 0
sw $t3, _t2_main
lw $t4, _t3_main
lw $t4, _t1_main
sw $t4, _t3_main
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $t5, _t2_main
sw $t5, 0($a0)
addi $a0, $a0, -4
lw $t6, _t3_main
sw $t6, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printPreorder
addu $sp, $fp, $0
lw $t7, _t4_main
move $t7, $v1
sw $t7, _t4_main
li $v0, 4
la $a0, cout_32
syscall
li $v0, 4
la $a0, cout_33
syscall
lw $t8, _t5_main
lw $t9, arr_size_global
li $s0, 1
sub $t8, $t9, $s0
sw $t8, _t5_main
lw $s1, _t6_main
li $s1, 0
sw $s1, _t6_main
lw $s2, _t7_main
lw $s2, _t5_main
sw $s2, _t7_main
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s3, _t6_main
sw $s3, 0($a0)
addi $a0, $a0, -4
lw $s4, _t7_main
sw $s4, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $s5, _t8_main
move $s5, $v1
sw $s5, _t8_main
li $v0, 4
la $a0, cout_41
syscall
li $v0, 4
la $a0, cout_42
syscall
lw $s6, _t9_main
lw $s7, arr_size_global
li $t0, 1
sub $s6, $s7, $t0
sw $s6, _t9_main
lw $t1, _t10_main
li $t1, 0
sw $t1, _t10_main
lw $t2, _t11_main
lw $t2, _t9_main
sw $t2, _t11_main
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $t3, _t10_main
sw $t3, 0($a0)
addi $a0, $a0, -4
lw $t4, _t11_main
sw $t4, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printPostorder
addu $sp, $fp, $0
lw $t5, _t12_main
move $t5, $v1
sw $t5, _t12_main
lw $t6, _t13_main
li $t6, 0
sw $t6, _t13_main
lw $t7, _t13_main
addu $v1, $t7, $0
lw $ra, 0($sp)
lw $fp, -4($sp)
li $v0, 10
syscall
lw $ra, 0($sp)
lw $fp, -4($sp)
li $v0, 10
syscall



printInorder:
addi $sp, $sp, -52
sw $ra, 0($sp)
sw $fp, -4($sp)
addu $fp, $0, $sp
lw $t8, 60($sp)
lw $t9, 56($sp)
bgt $t8, $t9, L_56
b L_57
L_56:
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
L_57:
lw $s0, 52($sp)
lw $s1, 60($sp)
li $s2, 2
mul $s0, $s1, $s2
sw $s0, 52($sp)
lw $s3, 44($sp)
lw $s4, 52($sp)
addi $s3, $s4, 1
sw $s3, 44($sp)
lw $s5, 40($sp)
lw $s5, 44($sp)
sw $s5, 40($sp)
lw $s6, 36($sp)
lw $s6, 56($sp)
sw $s6, 36($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s7, 40($sp)
sw $s7, 0($a0)
addi $a0, $a0, -4
lw $t0, 36($sp)
sw $t0, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $t1, 32($sp)
move $t1, $v1
sw $t1, 32($sp)
lw $t2, 28($sp)
li $t2, 0
sw $t2, 28($sp)
lw $t3, 24($sp)
lw $t4, 60($sp)
li $t5, 1
mul $t3, $t4, $t5
sw $t3, 24($sp)
lw $t6, 28($sp)
lw $t7, 28($sp)
lw $t8, 24($sp)
add $t6, $t7, $t8
sw $t6, 28($sp)
lw $t9, 28($sp)
lw $s0, 28($sp)
li $s1, 4
mul $t9, $s0, $s1
sw $t9, 28($sp)
lw $s2, 48($sp)
la $s3, arr_global
lw $s4, 28($sp)
addu $s3, $s3, $s4
lw $s3, ($s3)
move $s2, $s3
sw $s2, 48($sp)
li $v0, 1
lw $a0, 48($sp)
syscall
li $v0, 4
la $a0, cout_71
syscall
lw $s5, 20($sp)
lw $s6, 60($sp)
li $s7, 2
mul $s5, $s6, $s7
sw $s5, 20($sp)
lw $t0, 16($sp)
lw $t1, 20($sp)
addi $t0, $t1, 2
sw $t0, 16($sp)
lw $t2, 12($sp)
lw $t2, 16($sp)
sw $t2, 12($sp)
lw $t3, 8($sp)
lw $t3, 56($sp)
sw $t3, 8($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $t4, 12($sp)
sw $t4, 0($a0)
addi $a0, $a0, -4
lw $t5, 8($sp)
sw $t5, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $t6, 4($sp)
move $t6, $v1
sw $t6, 4($sp)
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
printPostorder:
addi $sp, $sp, -52
sw $ra, 0($sp)
sw $fp, -4($sp)
addu $fp, $0, $sp
lw $t7, 60($sp)
lw $t8, 56($sp)
bgt $t7, $t8, L_84
b L_85
L_84:
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
L_85:
lw $t9, 52($sp)
lw $s0, 60($sp)
li $s1, 2
mul $t9, $s0, $s1
sw $t9, 52($sp)
lw $s2, 44($sp)
lw $s3, 52($sp)
addi $s2, $s3, 1
sw $s2, 44($sp)
lw $s4, 40($sp)
lw $s4, 44($sp)
sw $s4, 40($sp)
lw $s5, 36($sp)
lw $s5, 56($sp)
sw $s5, 36($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s6, 40($sp)
sw $s6, 0($a0)
addi $a0, $a0, -4
lw $s7, 36($sp)
sw $s7, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $t0, 32($sp)
move $t0, $v1
sw $t0, 32($sp)
lw $t1, 28($sp)
lw $t2, 60($sp)
li $t3, 2
mul $t1, $t2, $t3
sw $t1, 28($sp)
lw $t4, 24($sp)
lw $t5, 28($sp)
addi $t4, $t5, 2
sw $t4, 24($sp)
lw $t6, 20($sp)
lw $t6, 24($sp)
sw $t6, 20($sp)
lw $t7, 16($sp)
lw $t7, 56($sp)
sw $t7, 16($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $t8, 20($sp)
sw $t8, 0($a0)
addi $a0, $a0, -4
lw $t9, 16($sp)
sw $t9, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $s0, 12($sp)
move $s0, $v1
sw $s0, 12($sp)
lw $s1, 8($sp)
li $s1, 0
sw $s1, 8($sp)
lw $s2, 4($sp)
lw $s3, 60($sp)
li $s4, 1
mul $s2, $s3, $s4
sw $s2, 4($sp)
lw $s5, 8($sp)
lw $s6, 8($sp)
lw $s7, 4($sp)
add $s5, $s6, $s7
sw $s5, 8($sp)
lw $t0, 8($sp)
lw $t1, 8($sp)
li $t2, 4
mul $t0, $t1, $t2
sw $t0, 8($sp)
lw $t3, 48($sp)
la $t4, arr_global
lw $t5, 8($sp)
addu $t4, $t4, $t5
lw $t4, ($t4)
move $t3, $t4
sw $t3, 48($sp)
li $v0, 1
lw $a0, 48($sp)
syscall
li $v0, 4
la $a0, cout_107
syscall
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
printPreorder:
addi $sp, $sp, -52
sw $ra, 0($sp)
sw $fp, -4($sp)
addu $fp, $0, $sp
lw $t6, 60($sp)
lw $t7, 56($sp)
bgt $t6, $t7, L_112
b L_113
L_112:
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra
L_113:
lw $t8, 52($sp)
li $t8, 0
sw $t8, 52($sp)
lw $t9, 44($sp)
lw $s0, 60($sp)
li $s1, 1
mul $t9, $s0, $s1
sw $t9, 44($sp)
lw $s2, 52($sp)
lw $s3, 52($sp)
lw $s4, 44($sp)
add $s2, $s3, $s4
sw $s2, 52($sp)
lw $s5, 52($sp)
lw $s6, 52($sp)
li $s7, 4
mul $s5, $s6, $s7
sw $s5, 52($sp)
lw $t0, 48($sp)
la $t1, arr_global
lw $t2, 52($sp)
addu $t1, $t1, $t2
lw $t1, ($t1)
move $t0, $t1
sw $t0, 48($sp)
li $v0, 1
lw $a0, 48($sp)
syscall
li $v0, 4
la $a0, cout_119
syscall
lw $t3, 40($sp)
lw $t4, 60($sp)
li $t5, 2
mul $t3, $t4, $t5
sw $t3, 40($sp)
lw $t6, 36($sp)
lw $t7, 40($sp)
addi $t6, $t7, 1
sw $t6, 36($sp)
lw $t8, 32($sp)
lw $t8, 36($sp)
sw $t8, 32($sp)
lw $t9, 28($sp)
lw $t9, 56($sp)
sw $t9, 28($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $s0, 32($sp)
sw $s0, 0($a0)
addi $a0, $a0, -4
lw $s1, 28($sp)
sw $s1, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $s2, 24($sp)
move $s2, $v1
sw $s2, 24($sp)
lw $s3, 20($sp)
lw $s4, 60($sp)
li $s5, 2
mul $s3, $s4, $s5
sw $s3, 20($sp)
lw $s6, 16($sp)
lw $s7, 20($sp)
addi $s6, $s7, 2
sw $s6, 16($sp)
lw $t0, 12($sp)
lw $t0, 16($sp)
sw $t0, 12($sp)
lw $t1, 8($sp)
lw $t1, 56($sp)
sw $t1, 8($sp)
addu $fp, $sp, $0
addi $a0, $sp, -8
lw $t2, 12($sp)
sw $t2, 0($a0)
addi $a0, $a0, -4
lw $t3, 8($sp)
sw $t3, 0($a0)
addi $a0, $a0, -4
addu $sp, $a0, $0
jal printInorder
addu $sp, $fp, $0
lw $t4, 4($sp)
move $t4, $v1
sw $t4, 4($sp)
lw $ra, 0($sp)
lw $fp, -4($sp)
jr $ra


.data

arr_global: .word 4, 2, 6, 1, 3, 5, 7
arr_size_global: .word 7
cout_24: .asciiz "The PreOrder Traversal is:\n"
cout_32: .asciiz "\n"
cout_33: .asciiz "The InOrder Traversal is:\n"
cout_41: .asciiz "\n"
cout_42: .asciiz "The PostOrder Traversal is:\n"
cout_71: .asciiz " "
cout_107: .asciiz " "
cout_119: .asciiz " "
_t1_global: .word 0
_t2_global: .word 0
_t1_main: .word 0
_t2_main: .word 0
_t3_main: .word 0
_t4_main: .word 0
_t5_main: .word 0
_t6_main: .word 0
_t7_main: .word 0
_t8_main: .word 0
_t9_main: .word 0
_t10_main: .word 0
_t11_main: .word 0
_t12_main: .word 0
_t13_main: .word 0
