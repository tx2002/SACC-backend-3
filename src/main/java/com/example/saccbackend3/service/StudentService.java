package com.example.saccbackend3.service;


import com.example.saccbackend3.entity.Student;
import com.example.saccbackend3.mapper.StudentMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 *
 * @author TX
 * @date 2022/3/24 12:43
 */
@Service
public interface StudentService {

    //新增一个学生
    Boolean addStudent(Student student);

    //根据id删除一个学生
    Boolean deleteStudentById(String id);

    //更新学生
    Boolean updateStudent(Student student);

    //查找所有学生
    List<Student> listStudent();

    //根据年龄段查找学生
    List<Student> listStudentByAges(Integer age1, Integer age2);

}
