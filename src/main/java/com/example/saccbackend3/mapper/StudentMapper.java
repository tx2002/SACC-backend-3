package com.example.saccbackend3.mapper;

import com.example.saccbackend3.entity.Student;
import org.apache.ibatis.annotations.Mapper;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 *
 * @author TX
 * @date 2022/3/24 12:59
 */
@Mapper
@Repository
public interface StudentMapper {
    //新增一个学生
    public Integer addStudent(Student student);

    //根据id删除一个学生
    public Integer deleteStudentById(String id);

    //更新学生
    public Integer updateStudent(Student student);

    //查找所有学生
    public List<Student> listStudent();

    //根据年龄段查找学生
    public List<Student> listStudentByAges(Integer age1, Integer age2);
}
