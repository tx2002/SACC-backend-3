package com.example.saccbackend3.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 *
 * @author TX
 * @date 2022/3/24 11:35
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Student {
    //学号
    private String id;
    //姓名
    private String name;
    //性别
    private String sex;
    //年龄
    private String age;
    //邮箱
    private String email;
}
