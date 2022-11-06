/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/
#include "InterruptRoutines.h"
#include "project.h"

uint8 ch_received;

CY_ISR(Custom_ISR){
    
    ch_received = UART_GetChar();
    
    switch(ch_received){
        case 's':
        case 'S':
            Pin_LED_Write(0);
        break;
        case 'b':
        case 'B':
            Pin_LED_Write(1);
        break;
        default:
            break;
    }
}
            
            

/* [] END OF FILE */
