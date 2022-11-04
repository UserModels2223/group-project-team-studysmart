# Training accuracy plot 
ggplot(training_acc,aes(x=fct_inorder(subject), y=accuracy, fill=Condition)) + 
  +     geom_bar(stat="identity", position="dodge")+
  +     labs(main="Training accuracy per subject: Baseline vs. Context", x="Subject", y="Accuracy") +
  +     scale_fill_manual(values=cbp1, labels=c("Baseline", "Context"))+
  +     ggtitle("Training accuracy per subject") + scale_y_continuous(limits=c(0,1))

training_acc <- data.frame(subject=c("9","9","11","11","18","18","38","38","45","45","80","80"), 
                           accuracy=c(0.74,0.8066,0.82,0.933,0.5933,0.6266,0.866,0.84,0.5866,0.566,0.82,0.7133),
                           Condition=LETTERS[1:2])

# Testing accuracy plot 
ggplot(testing_acc,aes(x=fct_inorder(subject), y=accuracy, fill=Condition)) + 
  +     geom_bar(stat="identity", position="dodge")+
  +     labs(main="Training accuracy per subject: Baseline vs. Context", x="Subject", y="Accuracy") +
  +     scale_fill_manual(values=cbp1, labels=c("Baseline", "Context"))+
  +     ggtitle("Testing accuracy per subject")

testing_acc <- data.frame(subject=c("9","9","11","11","18","18","38","38","45","45","80","80"), accuracy=c(0.8235,0.7619,1,1,0.95,0.7727,0.9545,1,0.8125,0.75,0.9545,0.8182),Condition=LETTERS[1:2])

# RT Plot 
ggplot(testing_RT,aes(x=fct_inorder(subject), y=RT, fill=Condition)) + 
  +     geom_bar(stat="identity", position="dodge")+
  +     labs(x="Subject", y="Response Time (ms)") +
  +     scale_fill_manual(values=cbp1, labels=c("Baseline", "Context"))+
  +     ggtitle("Response time per subject during testing") +
  +     geom_errorbar(aes(ymin=RT-SD, ymax=RT+SD), width=.2,
                      +                   position=position_dodge(.9)) 

testing_RT <- data.frame(subject=c("9","9","11","11","18","18","38","38","45","45","80","80"), RT=c(1959,2609,2353,2580,1246,1083,1059,1034,1959,3586,1509,3017),Condition=LETTERS[1:2], SD=c(1654,3009,2510,2289,805,870,647,646,890,1125,359,2334))